#!/usr/bin/env python3
"""cp_lib.py (v1.5, 2026-11-10) - reusable helpers for the 'cycling | running' coaching project.

Companion to analysis_tools.py (activity files -> reports / digest) and routes_tool.py (GPX route geometry).
This module collects everything else that was written ad hoc during the chats:
  PHYSICS    power <-> speed <-> wind model, critical-power sketches
  SUN        sunrise / sunset (NOAA approximation, DST-aware)
  PATCH      safe text patcher for the markdown files (every edit asserts that its target exists)
  FIT        inspection of FIT files: structure, laps, timer events, pauses, HRV / strap quality
  RIDE       10-min block tables, best windows (power, HR, distance, speed), decoupling, HR by power, effort finder
  RUN        splits, halves, tail paces, fastest windows (reps), HR plateaus / steps / zone time, loop length
  TESTS      4DP / Full Frontal report (sprints with a physics check, blocks, gaps, strap quality)
  CSV/DIGEST Strava activities.csv loader, weekly table, bests table, history_digest.md generator
Needs numpy; pandas (CSV/DIGEST); scipy (PHYSICS); fitparse (FIT; pip install fitparse --break-system-packages).
Usage:  import cp_lib as cp ; cp.speed_from_power(185, 0.004) ; python3 cp_lib.py --index   (prints the function index)
Conventions (see coach_notes.md): 'elapsed-based' = Strava power-curve convention (stopped/paused seconds count as 0 W);
'rolling'/'moving' = stopped seconds removed, coasting kept (Strava average-power convention).
"""
import math, re, os, io, gzip, collections
from datetime import datetime, timezone, date as _date
import numpy as np

# ----------------------------------------------------------------------------- CONFIG
CFG = dict(ftp=180.0,                                                 # working FTP (W) until the 60-min trainer test
           z2cap=135.0, tz="Europe/Berlin", home=(50.8438, 6.8942), sun_site=(50.94, 6.96),
           mass=72.0, cda=0.38, crr=0.005, rho=1.22, eta=0.98,           # rider+bike+kit 72 kg, hoods position, cool autumn air
           ride_hr_zones=(125, 150, 170, 182), run_hr_zones=(130, 160, 175, 190),
           zone_edges=(0, .55, .75, .90, 1.05, 1.20, 1.50, 99))          # Coggan, as fractions of FTP
G = 9.81


def _c(kw):
    return {**CFG, **kw}


def fmt_t(sec):
    """Seconds -> m:ss text (e.g. 1410 -> 23:30)."""
    sec = int(round(sec)); return "%d:%02d" % (sec // 60, sec % 60)


# ----------------------------------------------------------------------------- PHYSICS
def power_needed(v_kmh, grade=0.0, wind_kmh=0.0, **kw):
    """Pedal power (W) needed for ground speed v_kmh on a grade (fraction); wind_kmh > 0 = headwind."""
    c = _c(kw); v = v_kmh / 3.6; va = v + wind_kmh / 3.6
    aero = 0.5 * c["rho"] * c["cda"] * va * abs(va) * v
    return (aero + c["crr"] * c["mass"] * G * v + c["mass"] * G * grade * v) / c["eta"]


def speed_from_power(P, grade=0.0, wind_kmh=0.0, **kw):
    """Ground speed (km/h) for pedal power P (W). Example: speed_from_power(185, 0.004) -> about 29.8."""
    from scipy.optimize import brentq
    return brentq(lambda v: power_needed(v, grade, wind_kmh, **kw) - P, 1.0, 120.0)


def implied_headwind(P, v_kmh, grade=0.0, **kw):
    """Headwind (km/h, negative = tailwind) that the model needs to explain speed v_kmh at power P. Rough (CdA unknown): use a CdA range."""
    from scipy.optimize import brentq
    return brentq(lambda w: power_needed(v_kmh, grade, w, **kw) - P, -40.0, 60.0)


def effort_distance(P, minutes=20, grade=0.004, wind_kmh=0.0, **kw):
    """Distance (km) covered in `minutes` at constant power P: how long a corner-free stretch must be."""
    return speed_from_power(P, grade, wind_kmh, **kw) * minutes / 60.0


def distance_table(powers=(175, 180, 185, 190, 195), winds=(-15, -10, 0, 10, 15), minutes=20, grade=0.004, show=True, **kw):
    """Table of effort distance by power (rows) and wind (columns, + = headwind km/h). Returns {power: [km,...]}."""
    out = {P: [effort_distance(P, minutes, grade, w, **kw) for w in winds] for P in powers}
    if show:
        print("%d-min distance (km), grade %+.1f%%, wind km/h (+ = head): %s" % (minutes, grade * 100, winds))
        for P, row in out.items(): print("  %3d W | %s" % (P, " | ".join("%5.1f" % x for x in row)))
    return out


def cp_fit(points):
    """Two-parameter critical-power sketch from [(seconds, watts), ...] (>= 2 points; least squares of work vs time).
    Returns (CP_watts, Wprime_joules). Crude: assumes the points are near-maximal efforts between ~2 and 20 min."""
    t = np.array([p[0] for p in points], float); w = np.array([p[1] for p in points], float) * t
    cp, wp = np.polyfit(t, w, 1)
    return float(cp), float(wp)


def cp_predict(cp, wprime, seconds):
    """Power (W) the critical-power sketch predicts for an effort of `seconds` (CP + W'/t)."""
    return cp + wprime / seconds


# ----------------------------------------------------------------------------- SUN
def sun_times(d, lat=None, lon=None, tz=None, zenith=90.833):
    """(sunrise, sunset) as 'HH:MM' local time for date d (NOAA approximation, DST-aware). zenith=96 gives civil twilight (dawn, dusk)."""
    from zoneinfo import ZoneInfo
    lat = CFG["sun_site"][0] if lat is None else lat; lon = CFG["sun_site"][1] if lon is None else lon
    tz = tz or CFG["tz"]
    off = datetime(d.year, d.month, d.day, 12, tzinfo=ZoneInfo(tz)).utcoffset().total_seconds() / 3600
    n = d.timetuple().tm_yday; g = 2 * math.pi / 365 * (n - 1)
    eqt = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g) - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    decl = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g) + 0.000907 * math.sin(2 * g)
            - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    la = math.radians(lat)
    ha = math.degrees(math.acos(math.cos(math.radians(zenith)) / (math.cos(la) * math.cos(decl)) - math.tan(la) * math.tan(decl)))
    f = lambda m: "%02d:%02d" % divmod(int(round(m + off * 60)) % 1440, 60)
    return f(720 - 4 * (lon + ha) - eqt), f(720 - 4 * (lon - ha) - eqt)


# ----------------------------------------------------------------------------- PATCH
class Patch:
    """Safe edits of a text file. Every edit must find its target (exactly once unless count is given), otherwise it is recorded as a failure.
        p = Patch('coach_notes.md'); p.rep('old text', 'new text', 'tag'); p.insert_after('- [stated] Wahoo', 'new line'); p.save('out.md')
    save() writes nothing and returns the failures if strict=True and any edit failed."""
    def __init__(self, path=None, text=None, strict=True):
        self.path = path; self.strict = strict; self.fails = []; self.n_ok = 0
        self.text = text if text is not None else open(path, encoding="utf-8").read()

    def _fail(self, tag, why, what):
        self.fails.append("%s: %s (%s)" % (tag or what[:40], why, what[:60].replace("\n", " ")))

    def rep(self, old, new, tag="", count=1):
        n = self.text.count(old)
        if n == 0: return self._fail(tag, "not found", old)
        if count == 1 and n != 1: return self._fail(tag, "found %d times, not unique" % n, old)
        self.text = self.text.replace(old, new, count if count else -1); self.n_ok += 1

    def _line(self, startswith, tag):
        m = re.search(r"^" + re.escape(startswith) + r".*$", self.text, re.M)
        if not m: self._fail(tag, "line not found", startswith)
        return m

    def insert_after(self, startswith, new, tag=""):
        m = self._line(startswith, tag)
        if m: self.text = self.text[:m.end()] + "\n" + new + self.text[m.end():]; self.n_ok += 1

    def line_replace(self, startswith, new, tag=""):
        m = self._line(startswith, tag)
        if m: self.text = self.text[:m.start()] + new + self.text[m.end():]; self.n_ok += 1

    def delete_line(self, startswith, tag=""):
        m = self._line(startswith, tag)
        if m: self.text = self.text[:m.start()] + self.text[m.end() + 1:]; self.n_ok += 1

    def save(self, out=None):
        if self.fails and self.strict:
            print("NOT SAVED, %d edit(s) failed:" % len(self.fails)); [print("  -", f) for f in self.fails]; return self.fails
        open(out or self.path, "w", encoding="utf-8").write(self.text)
        print("saved %s: %d edits ok, %d failed" % (out or self.path, self.n_ok, len(self.fails))); return self.fails


# ----------------------------------------------------------------------------- FIT
def _fitfile(path):
    from fitparse import FitFile
    raw = gzip.open(path, "rb").read() if str(path).lower().endswith(".gz") else open(path, "rb").read()
    return FitFile(io.BytesIO(raw))


def _local(ts, tz=None):
    from zoneinfo import ZoneInfo
    return ts.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(tz or CFG["tz"]))


def fit_inspect(path, show=True):
    """First look at a FIT file: producer/device, sport, session summary, record channels and counts, time span, gaps, timer events, laps, HRV."""
    cnt = collections.Counter(m.name for m in _fitfile(path).get_messages())
    info = {"messages": dict(cnt)}
    for m in _fitfile(path).get_messages("file_id"):
        d = {k: v for k, v in m.get_values().items() if v is not None}
        info["device"] = {k: d.get(k) for k in ("manufacturer", "garmin_product", "product", "type", "time_created") if k in d}; break
    for m in _fitfile(path).get_messages("device_info"):
        d = m.get_values()
        if d.get("software_version"): info["software"] = d["software_version"]; break
    for m in _fitfile(path).get_messages("session"):
        d = {k: v for k, v in m.get_values().items() if v is not None}
        keys = ("sport", "sub_sport", "start_time", "total_elapsed_time", "total_timer_time", "total_distance", "total_ascent", "avg_power", "max_power",
                "normalized_power", "avg_heart_rate", "max_heart_rate", "avg_cadence", "avg_temperature", "total_work", "threshold_power")
        info["session"] = {k: d[k] for k in keys if k in d}; break
    recs = [m.get_values() for m in _fitfile(path).get_messages("record")]
    fields = collections.Counter(k for r in recs for k, v in r.items() if v is not None and not k.startswith("unknown"))
    ts = np.array(sorted({r["timestamp"].replace(tzinfo=timezone.utc).timestamp() for r in recs if r.get("timestamp")}))
    info.update(records=len(recs), fields=dict(fields), n_laps=cnt.get("lap", 0), n_hrv=cnt.get("hrv", 0))
    if len(ts):
        dt = np.diff(ts)
        info.update(start_utc=datetime.fromtimestamp(ts[0], timezone.utc), end_utc=datetime.fromtimestamp(ts[-1], timezone.utc),
                    span_min=(ts[-1] - ts[0]) / 60, gaps=int((dt > 1.5).sum()), max_gap_s=float(dt.max()) if len(dt) else 0.0)
    ev = collections.Counter((m.get_value("event"), m.get_value("event_type"), m.get_value("timer_trigger")) for m in _fitfile(path).get_messages("event"))
    info["events"] = {"/".join(str(x) for x in k if x is not None): v for k, v in ev.items()}
    if show:
        for k, v in info.items(): print("%-9s %s" % (k, v))
    return info


def fit_laps(path, tz=None):
    """Lap table (lap button / auto laps): start (local), elapsed, timer, distance, power, HR, cadence, ascent, work, trigger. Needs pandas."""
    import pandas as pd
    rows = []
    for i, m in enumerate(_fitfile(path).get_messages("lap")):
        d = m.get_values()
        rows.append(dict(lap=i + 1, start=_local(d["start_time"], tz).strftime("%H:%M:%S") if d.get("start_time") else None,
                         elapsed_s=d.get("total_elapsed_time"), timer_s=d.get("total_timer_time"), dist_m=d.get("total_distance"),
                         avg_w=d.get("avg_power"), np_w=d.get("normalized_power"), max_w=d.get("max_power"),
                         avg_hr=d.get("avg_heart_rate"), max_hr=d.get("max_heart_rate"), avg_cad=d.get("avg_cadence"),
                         ascent=d.get("total_ascent"), work_kj=(d.get("total_work") or 0) / 1000.0, trigger=d.get("lap_trigger")))
    return pd.DataFrame(rows)


def fit_events(path, tz=None):
    """Timer events (start / stop_all with trigger auto|manual), markers, off-course notices. Needs pandas."""
    import pandas as pd
    rows = []; t0 = None
    for m in _fitfile(path).get_messages("event"):
        d = m.get_values(); ts = d.get("timestamp")
        if ts is None: continue
        if t0 is None: t0 = ts
        rows.append(dict(time=_local(ts, tz).strftime("%H:%M:%S"), offset_s=(ts - t0).total_seconds(), event=d.get("event"),
                         type=d.get("event_type"), trigger=d.get("timer_trigger")))
    return pd.DataFrame(rows)


def fit_pauses(path):
    """Timer pauses: from each stop_all to the next start: offset into the file, duration, and what triggered the stop (auto / manual)."""
    import pandas as pd
    ev = [(m.get_value("timestamp"), m.get_value("event_type"), m.get_value("timer_trigger")) for m in _fitfile(path).get_messages("event")
          if m.get_value("event") == "timer"]
    if not ev: return pd.DataFrame(columns=["offset_s", "duration_s", "trigger"])
    t0 = ev[0][0]; rows = []
    for i, (ts, typ, trig) in enumerate(ev):
        if typ in ("stop_all", "stop") and i + 1 < len(ev):
            rows.append(dict(offset_s=(ts - t0).total_seconds(), duration_s=(ev[i + 1][0] - ts).total_seconds(), trigger=trig))
    return pd.DataFrame(rows)


def hrv_quality(path, win_s=60, tol=0.25, flag_pct=5.0):
    """Beat-to-beat (RR) quality from the FIT 'hrv' messages (Garmin ride files; Strava-made files have none).
    A beat is an artefact if it deviates more than `tol` from the median of its 7 neighbours (or is outside 0.3-2.0 s).
    Returns (DataFrame per window: start_min, beats, artefact_pct, hr_from_rr, flag), summary dict). RR time runs on cumulative RR (values > 3 s are junk and
    left out of the time axis), so it can drift a little against the record timeline. A loosening strap shows up as rising artefact_pct / missing beats."""
    import pandas as pd
    rr = []
    for m in _fitfile(path).get_messages("hrv"):
        rr.extend([x for x in (m.get_value("time") or ()) if x is not None])
    rr = np.array(rr, float)
    if len(rr) < 20: return pd.DataFrame(), {"beats": int(len(rr))}
    med = np.array([np.median(rr[max(0, i - 3):i + 4]) for i in range(len(rr))])
    bad = (np.abs(rr - med) > tol * med) | (rr < 0.3) | (rr > 2.0)
    tt = np.cumsum(np.where(rr > 3.0, 0.0, rr)); rows = []          # junk values (Edge 540 files hold some of 6-58 s) must not stretch time
    for k in range(int(tt[-1] // win_s) + 1):
        m = (tt >= k * win_s) & (tt < (k + 1) * win_s)
        if m.sum() == 0: continue
        pct = bad[m].mean() * 100
        rows.append(dict(start_min=k * win_s / 60, beats=int(m.sum()), artefact_pct=round(pct, 1), hr_from_rr=round(60 / np.mean(rr[m & ~bad]), 0) if (m & ~bad).any() else np.nan, flag=pct > flag_pct))
    df = pd.DataFrame(rows)
    return df, {"beats": int(len(rr)), "artefact_pct": round(bad.mean() * 100, 2), "flagged_windows": int(df["flag"].sum()), "windows": int(len(df))}


# ----------------------------------------------------------------------------- LOADING (uses analysis_tools.py)
_AT = None


def _at():
    global _AT
    if _AT is None:
        import sys, importlib
        here = os.path.dirname(os.path.abspath(__file__))
        if here not in sys.path: sys.path.insert(0, here)
        _AT = importlib.import_module("analysis_tools")
    return _AT


def _ffill(x):
    x = np.asarray(x, float); ok = np.isfinite(x)
    if not ok.any(): return x
    idx = np.where(ok, np.arange(len(x)), 0); np.maximum.accumulate(idx, out=idx); return x[idx]


def load_activity(path):
    """Load a GPX / FIT / FIT.GZ activity. Returns (a, ex, tl): a = [t, lat, lon, ele, power, hr, cadence, temp] per record,
    ex = recorded extras (dist, speed) for FIT, tl = 1 Hz timeline dict (P, H, C, T, E, S, D, rec) with speed and distance filled."""
    at = _at(); a, ex = at.load_any(path); at._EX = ex
    tl = at.timeline(a, ex); at.ensure_speed(tl, a)
    if not np.isfinite(tl["D"]).any():                       # GPX: build distance from positions
        d = at.haversine(a[:-1, 1], a[:-1, 2], a[1:, 1], a[1:, 2]); cum = np.concatenate([[0], np.cumsum(d)])
        D = np.full(len(tl["rec"]), np.nan); D[(a[:, 0] - a[0, 0]).astype(int)] = cum; tl["D"] = D
    return a, ex, tl


# ----------------------------------------------------------------------------- RIDE
def ride_blocks(tl, minutes=10, thr=1.0):
    """Table of consecutive blocks of MOVING time (stops removed): avg W, NP, HR avg/max, pedalling cadence. Returns list of dicts."""
    at = _at(); mv = at.moving_mask(tl, thr)
    P = np.nan_to_num(tl["P"])[mv]; H = tl["H"][mv]; C = tl["C"][mv]; n = int(minutes * 60); rows = []
    for k in range(0, len(P), n):
        sl = slice(k, k + n); p = P[sl]; h = H[sl]; c = C[sl]
        if len(p) < 60 and rows: continue          # ignore a tail block shorter than 1 min
        rows.append(dict(block=len(rows) + 1, start_min=k / 60.0, minutes=len(p) / 60.0, avg_w=float(p.mean()),
                         np_w=float(at.norm_power(p)) if len(p) >= 30 else float("nan"),
                         hr_avg=float(np.nanmean(h)) if np.isfinite(h).any() else float("nan"),
                         hr_max=float(np.nanmax(h)) if np.isfinite(h).any() else float("nan"),
                         cad=float(np.nanmean(c[c > 0])) if (c > 0).any() else float("nan")))
    return rows


def best_window(tl, dur_s, basis="elapsed", thr=1.0):
    """Best mean-power window of dur_s seconds. basis='elapsed' (Strava curve: stops = 0 W) or 'moving' (stops removed, coasting kept).
    Returns dict: avg_w, np_w, start/end second (1 Hz timeline), wall_s, dist_km, speed_kmh, HR avg / first half / second half / last minute, cadence."""
    at = _at(); P = np.nan_to_num(tl["P"]); rec = tl["rec"]
    if basis == "elapsed": idx = np.arange(len(P)); x = np.where(rec, P, 0.0)
    else: mv = at.moving_mask(tl, thr); idx = np.where(mv)[0]; x = P[mv]
    if len(x) < dur_s: return None
    cs = np.cumsum(np.insert(x, 0, 0.0)); avg = (cs[dur_s:] - cs[:-dur_s]) / dur_s; i = int(np.argmax(avg))
    win = idx[i:i + dur_s]; s, e = int(win[0]), int(win[-1]); D = _ffill(tl["D"]); wall = e - s + 1
    h = tl["H"][win]; c = tl["C"][win]; half = len(h) // 2
    f = lambda z: float(np.nanmean(z)) if np.isfinite(z).any() else float("nan")
    return dict(avg_w=float(avg[i]), np_w=float(at.norm_power(x[i:i + dur_s])) if dur_s >= 30 else float("nan"), start_s=s, end_s=e, start_min=s / 60.0,
                wall_s=wall, dist_km=float((D[e] - D[s]) / 1000), speed_kmh=float((D[e] - D[s]) / 1000 / (wall / 3600)),
                hr_avg=f(h), hr_first_half=f(h[:half]), hr_second_half=f(h[half:]), hr_last_min=f(h[-60:]), cad=f(c[c > 0]) if (c > 0).any() else float("nan"))


def decoupling(p, h):
    """Aerobic decoupling over a power / HR series (same length, e.g. moving seconds): efficiency factor (NP/HR) of the 1st vs 2nd half.
    Positive % = HR drifts up relative to power. Only meaningful for steady rides > 60 min, not for rides with intervals."""
    at = _at(); p = np.asarray(p, float); h = np.asarray(h, float); ok = np.isfinite(h); p = p[ok]; h = h[ok]
    if len(p) < 600: return None
    m = len(p) // 2; ef = lambda pp, hh: at.norm_power(pp) / np.mean(hh)
    e1, e2 = ef(p[:m], h[:m]), ef(p[m:], h[m:])
    return dict(ef_first=e1, ef_second=e2, decoupling_pct=(e1 - e2) / e1 * 100, w_first=float(p[:m].mean()), w_second=float(p[m:].mean()),
                hr_first=float(h[:m].mean()), hr_second=float(h[m:].mean()))


def hr_by_power(p, h, edges=(100, 136, 156, 181)):
    """Mean HR and seconds per power band (default bands: <100, 100-135, 136-155, 156-180, >180 W). Returns list of (label, seconds, hr)."""
    p = np.asarray(p, float); h = np.asarray(h, float); e = [-1] + list(edges) + [10 ** 5]; out = []
    for lo, hi in zip(e[:-1], e[1:]):
        m = (p > lo) & (p <= hi) & np.isfinite(h)
        out.append(("%s-%s W" % (max(lo + 1, 0), hi if hi < 10 ** 5 else "+"), int(m.sum()), float(h[m].mean()) if m.any() else float("nan")))
    return out


def find_efforts(p, start_w=None, hold_w=None, min_len=8, ftp=None):
    """Find hard efforts in a power series (1 Hz): start when 5-s mean >= start_w (default 1.2 x FTP), continue while >= hold_w (default 0.97 x FTP),
    keep those >= min_len s. Returns list of dicts (start_s, dur_s, avg_w, max_w) in series time."""
    ftp = ftp or CFG["ftp"]; start_w = start_w or 1.2 * ftp; hold_w = hold_w or 0.97 * ftp
    p = np.nan_to_num(np.asarray(p, float)); sm = np.convolve(p, np.ones(5) / 5, mode="same"); out = []; i = 0
    while i < len(sm):
        if sm[i] >= start_w:
            j = i
            while j < len(sm) and sm[j] >= hold_w: j += 1
            if j - i >= min_len: out.append(dict(start_s=i, dur_s=j - i, avg_w=float(p[i:j].mean()), max_w=float(p[i:j].max())))
            i = j
        else: i += 1
    return out


def ride_session(path, ftp=None, block_min=10, windows=(300, 600, 1200, 1800, 3600), show=True):
    """One-call post-ride summary of a ride file: totals, 10-min blocks, best windows (elapsed + moving) with HR/speed, decoupling, HR by power, efforts."""
    at = _at(); ftp = ftp or CFG["ftp"]; a, ex, tl = load_activity(path)
    m = at.ride_metrics(tl, a, ftp, CFG["z2cap"]); mv = at.moving_mask(tl); p = np.nan_to_num(tl["P"])[mv]; h = tl["H"][mv]
    res = dict(metrics=m, blocks=ride_blocks(tl, block_min),
               windows={d: {"elapsed": best_window(tl, d, "elapsed"), "moving": best_window(tl, d, "moving")} for d in windows},
               decoupling=decoupling(p, h), hr_by_power=hr_by_power(p, h), efforts=find_efforts(p, ftp=ftp))
    if show:
        print("elapsed %s | recorded %s | moving %s | avg %.0f W (moving) NP %.0f IF %.2f VI %.2f | max %.0f W | HR avg %.0f max %.0f" % (
            fmt_t(m["elapsed_s"]), fmt_t(m["recorded_s"]), fmt_t(m["moving_s"]), m["avg_w_moving"], m["np_w"], m["if_"], m["vi"], m["max_w"], m.get("hr_avg", float("nan")), m.get("hr_max", float("nan"))))
        print("blocks of %d min moving time: " % block_min + " | ".join("%d: %.0fW (NP %.0f) HR %.0f%s" % (b["block"], b["avg_w"], b["np_w"], b["hr_avg"], "" if b["minutes"] > block_min - 0.1 else " [%.0f min]" % b["minutes"]) for b in res["blocks"]))
        for d, v in res["windows"].items():
            for basis in ("elapsed", "moving"):
                w = v[basis]
                if w: print("  best %4d s %-7s %.0f W (NP %.0f) at min %.1f  HR %.0f (halves %.0f/%.0f)  %.2f km %.1f km/h" % (d, basis, w["avg_w"], w["np_w"], w["start_min"], w["hr_avg"], w["hr_first_half"], w["hr_second_half"], w["dist_km"], w["speed_kmh"]))
        if res["decoupling"]: print("decoupling %.1f%% (EF %.2f -> %.2f)" % (res["decoupling"]["decoupling_pct"], res["decoupling"]["ef_first"], res["decoupling"]["ef_second"]))
        print("HR by power: " + "; ".join("%s: %.0f bpm (%d s)" % (x[0], x[2], x[1]) for x in res["hr_by_power"]))
        print("efforts >= %.0f W: %d" % (1.2 * ftp, len(res["efforts"])))
    return res


# ----------------------------------------------------------------------------- RUN
def run_series(path_or_a, ex=None):
    """Distance-based series of a run: dict with t (s), dist (m, recorded distance if the file has it), mt (moving-time axis, pauses removed), hr, lat, lon.
    NOTE: use the distance field, not the speed field, of Strava-made FIT files."""
    at = _at()
    if isinstance(path_or_a, (str, os.PathLike)): a, ex = at.load_any(str(path_or_a))
    else: a = path_or_a; ex = ex or {}
    t = a[:, 0] - a[0, 0]; d = at.haversine(a[:-1, 1], a[:-1, 2], a[1:, 1], a[1:, 2]); cum = np.concatenate([[0], np.cumsum(d)])
    if ex.get("dist") is not None and np.isfinite(ex["dist"]).all(): cum = np.asarray(ex["dist"], float) - float(ex["dist"][0]); d = np.diff(cum)
    dt = np.diff(t); stop = (dt > 2.5) & (d / np.maximum(dt, 1) < 1.0); mt = np.concatenate([[0], np.cumsum(np.where(stop, 0.0, dt))])
    return dict(t=t, dist=cum, mt=mt, hr=a[:, 5], lat=a[:, 1], lon=a[:, 2])


def split_table(rs, step=1000):
    """Splits every `step` metres (moving time): from_m, to_m, time_s, pace_s_km, hr_avg, hr_max. The last partial split (>= 100 m) is included."""
    dist, mt, hr = rs["dist"], rs["mt"], rs["hr"]; tot = dist[-1]; rows = []; lo = 0.0
    while lo < tot - 1:
        hi = min(lo + step, tot)
        if hi - lo < 100 and rows: break
        t0, t1 = np.interp(lo, dist, mt), np.interp(hi, dist, mt); m = (dist >= lo) & (dist <= hi) & np.isfinite(hr)
        rows.append(dict(from_m=lo, to_m=hi, time_s=t1 - t0, pace_s_km=(t1 - t0) / ((hi - lo) / 1000), hr_avg=float(hr[m].mean()) if m.any() else float("nan"), hr_max=float(hr[m].max()) if m.any() else float("nan")))
        lo = hi
    return rows


def halves(rs, split_m=None):
    """First vs second part of a run (default: half distance): times, paces and how much faster the second part was (%, positive = negative split)."""
    tot = rs["dist"][-1]; s = split_m or tot / 2; tm = np.interp(s, rs["dist"], rs["mt"]); t_end = rs["mt"][-1]
    p1 = tm / (s / 1000); p2 = (t_end - tm) / ((tot - s) / 1000)
    return dict(first_s=tm, second_s=t_end - tm, first_pace=p1, second_pace=p2, faster_pct=(1 - p2 / p1) * 100)


def tail_paces(rs, lengths=(200, 400, 500, 1000)):
    """Time and pace over the last L metres of a run, for each L. Returns {L: (seconds, pace_s_km)}."""
    tot = rs["dist"][-1]; return {L: (rs["mt"][-1] - np.interp(tot - L, rs["dist"], rs["mt"]), (rs["mt"][-1] - np.interp(tot - L, rs["dist"], rs["mt"])) / (L / 1000)) for L in lengths}


def fastest_windows(rs, window_s=240, n=2):
    """Fastest non-overlapping windows of window_s seconds (for interval runs / reps): start (moving min), pace, distance, HR avg/max."""
    mt, dist, hr = rs["mt"], rs["dist"], rs["hr"]
    if mt[-1] < window_s: return []
    grid = np.arange(0, mt[-1] - window_s + 1.0); v = (np.interp(grid + window_s, mt, dist) - np.interp(grid, mt, dist)) / window_s; out = []
    for _ in range(n):
        if not np.isfinite(v).any() or np.nanmax(v) <= 0: break
        i = int(np.nanargmax(v)); m = (mt >= grid[i]) & (mt <= grid[i] + window_s) & np.isfinite(hr)
        out.append(dict(start_min=grid[i] / 60, pace_s_km=1000 / v[i], dist_m=v[i] * window_s, hr_avg=float(hr[m].mean()) if m.any() else float("nan"), hr_max=float(hr[m].max()) if m.any() else float("nan")))
        v[max(0, i - int(window_s)):i + int(window_s)] = np.nan
    return out


def hr_plateaus(hr, t=None, min_len=8):
    """Runs of >= min_len identical consecutive HR readings (possible held values / strap trouble) and the count of NaN seconds. Returns (list of (start_s, length, bpm), n_nan)."""
    hr = np.asarray(hr, float); t = np.arange(len(hr)) if t is None else np.asarray(t); out = []; run = 1
    for i in range(1, len(hr) + 1):
        if i < len(hr) and np.isfinite(hr[i]) and hr[i] == hr[i - 1]: run += 1
        else:
            if run >= min_len and np.isfinite(hr[i - 1]): out.append((float(t[i - run]), run, float(hr[i - 1])))
            run = 1
    return out, int(np.isnan(hr).sum())


def hr_steps(hr, win=10, thr=6.0):
    """Sudden HR steps (mean of the next `win` s vs the previous `win` s differs by >= thr bpm, at most one per minute). Returns list of (index_s, delta)."""
    hh = np.asarray(hr, float); hh = hh[np.isfinite(hh)]; out = []; last = -999
    for i in range(win, len(hh) - win):
        ch = hh[i:i + win].mean() - hh[i - win:i].mean()
        if abs(ch) >= thr and i - last > 60: out.append((i, float(ch))); last = i
    return out


def hr_zone_time(hr, edges=None):
    """Share of valid HR seconds per zone. edges = upper bounds of zones 1..n-1 (default: run zones 130/160/175/190). Returns list of fractions."""
    edges = edges or CFG["run_hr_zones"]; h = np.asarray(hr, float); h = h[np.isfinite(h)]; e = [0] + list(edges) + [999]
    return [float(((h >= lo) & (h < hi)).mean()) for lo, hi in zip(e[:-1], e[1:])]


def loop_length(rs, tol=25.0, min_m=400.0):
    """Length (m) of the first lap of a loop course: first return within `tol` m of the start after min_m metres (None if none)."""
    at = _at(); ds = at.haversine(rs["lat"][0], rs["lon"][0], rs["lat"], rs["lon"]); cand = np.where((rs["dist"] > min_m) & (ds < tol))[0]
    if not len(cand): return None
    j = cand[0] + int(np.argmin(ds[cand[0]:cand[0] + 60])); return float(rs["dist"][j])


def run_finish_report(path, step=1000, show=True):
    """One-call summary for a trial / race run: km splits with HR, 500 m splits, halves, tail paces, HR zone shares, HR plateaus, loop length."""
    rs = run_series(path); out = dict(splits=split_table(rs, step), splits_500=split_table(rs, 500), halves=halves(rs), tails=tail_paces(rs),
                                      zones=hr_zone_time(rs["hr"]), plateaus=hr_plateaus(rs["hr"], rs["t"]), loop_m=loop_length(rs))
    if show:
        print("distance %.3f km, moving %s" % (rs["dist"][-1] / 1000, fmt_t(rs["mt"][-1])))
        print("splits: " + " | ".join("%s HR %.0f" % (fmt_t(s["time_s"] * 1000 / (s["to_m"] - s["from_m"])), s["hr_avg"]) for s in out["splits"]))
        h = out["halves"]; print("halves: %s vs %s (%.1f%% faster 2nd)" % (fmt_t(h["first_s"]), fmt_t(h["second_s"]), h["faster_pct"]))
        print("tails: " + ", ".join("last %d m %s/km" % (L, fmt_t(v[1])) for L, v in out["tails"].items()))
        print("HR zone shares (run zones): " + " ".join("%.0f%%" % (x * 100) for x in out["zones"]))
        print("HR plateaus (>=8 identical): %s, NaN seconds %d; loop length %s m" % (["%.0fs x%d @%.0f" % x for x in out["plateaus"][0]], out["plateaus"][1], out["loop_m"]))
    return out


# ----------------------------------------------------------------------------- TESTS
def top_windows(p, dur_s, n=2, sep_s=60, lo=0, hi=None):
    """Best `n` non-overlapping mean-power windows of `dur_s` seconds in p[lo:hi] (at least `sep_s` apart). Returns a list of (start_index, mean_watts)."""
    p = np.nan_to_num(np.asarray(p, float)); hi = len(p) if hi is None else hi; x = p[lo:hi]
    if len(x) < dur_s: return []
    cs = np.cumsum(np.insert(x, 0, 0.0)); w = (cs[dur_s:] - cs[:-dur_s]) / dur_s; out = []
    for _ in range(n):
        i = int(np.argmax(w))
        if w[i] <= 0: break
        out.append((lo + i, float(w[i]))); w[max(0, i - sep_s - dur_s):i + sep_s + dur_s] = -1
    return out


def sprint_energy_check(tl, s, e, mass=None, cda=0.40, crr=None, rho=None, eta=None):
    """Plausibility check of a sprint's power (seconds s..e of the timeline): meter energy vs the physics needed for the measured acceleration plus drag.

    Returns dict(meter_kj, physics_kj, ratio). A ratio of about 0.8-1.25 is consistent with the speed sensor: 1 Hz speed, its 1-2 s lag and an
    assumed mass / CdA make +-20% normal, so this only catches gross meter errors. Single-sided meters (Stages) can be further off in all-out sprints."""
    c = CFG; mass = mass or c["mass"]; crr = crr or c["crr"]; rho = rho or c["rho"]; eta = eta or c["eta"]
    P = np.nan_to_num(tl["P"][s:e + 1]); v = np.nan_to_num(tl["S"][s:e + 1])
    e_meter = P.sum() * eta; dke = 0.5 * mass * (v[-1] ** 2 - v[0] ** 2)
    drag = float(np.sum(0.5 * rho * cda * v ** 3 + crr * mass * G * v))
    phys = dke + drag
    return dict(meter_kj=e_meter / 1000, physics_kj=phys / 1000, ratio=e_meter / phys if phys > 0 else float("nan"))


def _block(tl, s, dur, per=60):
    at = _at(); P = np.nan_to_num(tl["P"]); H = tl["H"]; C = tl["C"]; D = _ffill(tl["D"]); E = _ffill(tl["E"]) if "E" in tl else None
    e = s + dur - 1; p = P[s:e + 1]; h = H[s:e + 1]; c = C[s:e + 1]
    f = lambda z: float(np.nanmean(z)) if np.isfinite(z).any() else float("nan")
    seg = [p[i:i + per] for i in range(0, len(p), per)]
    out = dict(start_s=int(s), end_s=int(e), avg_w=float(p.mean()), np_w=float(at.norm_power(p)) if len(p) >= 30 else float("nan"), max_w=float(p.max()),
               hr_avg=f(h), hr_first_min=f(h[:60]), hr_last_min=f(h[-60:]), hr_max=float(np.nanmax(h)) if np.isfinite(h).any() else float("nan"),
               cad=f(c[c > 0]) if (c > 0).any() else float("nan"), km_from=float(D[s] / 1000), km_to=float(D[e] / 1000),
               speed_kmh=float((D[e] - D[s]) / 1000 / (dur / 3600)), profile_w=[round(float(x.mean())) for x in seg],
               profile_hr=[round(f(h[i:i + per])) if np.isfinite(h[i:i + per]).any() else None for i in range(0, len(p), per)])
    if E is not None and D[e] > D[s]: out["grade_pct"] = float((E[e] - E[s]) / (D[e] - D[s]) * 100)
    if per == 60 and len(seg) >= 4:
        mins = [x.mean() for x in seg if len(x) == per]
        out["cv_pct"] = float(np.std(mins) / np.mean(mins) * 100) if mins else float("nan")
    return out


def _gap(tl, s, e):
    P = np.nan_to_num(tl["P"][s:e]); rec = tl["rec"][s:e]
    return dict(start_s=int(s), end_s=int(e), seconds=int(e - s), stopped_s=int((~rec).sum()), avg_w_recorded=float(P[rec].mean()) if rec.any() else 0.0,
                s_150_200w=int((rec & (P >= 150) & (P < 200)).sum()), s_over_200w=int((rec & (P >= 200)).sum()))


def fit_series(path):
    """FIT -> dict(t=epoch seconds, p, hr, cad) of the record messages, for meter_offset()."""
    rows = [(m.get_value("timestamp"), m.get_value("power"), m.get_value("heart_rate"), m.get_value("cadence")) for m in _fitfile(path).get_messages("record")]
    rows = [r for r in rows if r[0] is not None]
    t = np.array([r[0].replace(tzinfo=timezone.utc).timestamp() for r in rows])
    f = lambda k: np.array([np.nan if r[k] is None else float(r[k]) for r in rows])
    return dict(t=t, p=f(1), hr=f(2), cad=f(3))


def stream_series(streams, start_local, tz=None):
    """Strava connector streams (dict with time, watts, heart_rate; any resolution) + the activity's start_local ('2026-11-06T15:51:40') ->
    dict(t=epoch seconds, p, hr). Copy a reduced-resolution stream (resolution <= ~300) into a JSON file to use it in the sandbox."""
    import pandas as pd
    t0 = pd.Timestamp(start_local).tz_localize(tz or CFG["tz"]).timestamp()
    return dict(t=t0 + np.asarray(streams["time"], float), p=np.asarray(streams.get("watts", []), float), hr=np.asarray(streams.get("heart_rate", []), float))


def meter_offset(ref, other, max_lag=180, steady_sd=15.0, bands=(60, 100, 120, 150, 200, 400), show=True):
    """Compare two power meters recorded at the same time (e.g. ref = Edge/Stages FIT, other = KICKR via MyWhoosh FIT or stream).
    Both are dicts from fit_series() / stream_series(). Aligns `other` by the HR cross-correlation (same strap; fallback power) within
    +-max_lag s, then compares each `other` sample with the ref 5-s mean around it. Steady samples = ref 9-s SD < steady_sd W.
    Returns dict(lag_s, r_hr, n, ratio, fit=(a, b) for other = a*ref + b on steady samples, bands=[(lo, hi, n, other, ref, diff, ratio)]).
    6 Nov: KICKR = 0.97 x Stages + 13 W (+8 to +11 W, ratio 1.04 at 190 W, 1.11 at 100 W); MyWhoosh's start time was 51 s off on one file."""
    t0 = int(np.floor(np.nanmin(ref["t"]))); n = int(np.ceil(np.nanmax(ref["t"]))) - t0 + 1
    P = np.full(n, np.nan); H = np.full(n, np.nan); k = (np.asarray(ref["t"]) - t0).astype(int)
    P[k] = ref["p"]; H[k] = ref["hr"]; P = np.nan_to_num(P)
    ot = np.asarray(other["t"]); op = np.asarray(other["p"], float); oh = np.asarray(other["hr"], float) if len(other.get("hr", [])) else np.full(len(ot), np.nan)
    def corr(lag, which):
        idx = np.round(ot + lag - t0).astype(int); ok = (idx >= 0) & (idx < n)
        a = oh[ok] if which == "hr" else op[ok]; b = H[idx[ok]] if which == "hr" else P[idx[ok]]; m = np.isfinite(a) & np.isfinite(b) & (a > 0) & (b > 0)
        return np.corrcoef(a[m], b[m])[0, 1] if m.sum() > 20 else -1
    which = "hr" if np.isfinite(oh).sum() > 20 and np.isfinite(H).sum() > 20 else "p"
    lags = np.arange(-max_lag, max_lag + 1); cs = np.array([corr(l, which) for l in lags]); lag = int(lags[np.argmax(cs)])
    idx = np.round(ot + lag - t0).astype(int); ok = (idx >= 4) & (idx < n - 4) & (op > 0)
    o = op[ok]; i = idx[ok]; r5 = np.array([P[x - 2:x + 3].mean() for x in i]); sd = np.array([P[x - 4:x + 5].std() for x in i]); st = sd < steady_sd
    rows = []
    for lo, hi in zip(bands[:-1], bands[1:]):
        m = st & (r5 >= lo) & (r5 < hi)
        if m.sum(): rows.append((lo, hi, int(m.sum()), float(o[m].mean()), float(r5[m].mean()), float(o[m].mean() - r5[m].mean()), float(o[m].mean() / r5[m].mean())))
    fit = tuple(np.linalg.lstsq(np.vstack([r5[st], np.ones(st.sum())]).T, o[st], rcond=None)[0]) if st.sum() > 10 else (np.nan, np.nan)
    res = dict(lag_s=lag, r_hr=float(cs.max()) if which == "hr" else np.nan, n=int(ok.sum()), ratio=float(o.mean() / r5.mean()), fit=fit, bands=rows)
    if show:
        print("lag %+d s (%s r %.3f), %d samples, overall ratio %.3f, steady fit other = %.3f x ref %+.1f W" % (lag, which, cs.max(), res["n"], res["ratio"], fit[0], fit[1]))
        for b in rows: print("  ref %3d-%3d W  n %3d  other %.1f  ref %.1f  diff %+.1f W  ratio %.3f" % b)
    return res


def hr_artefact_scan(tl, rules=((200.0, 45, 145.0, 5.0), (150.0, 120, 135.0, None)), merge_min=3.0, skip_min=5.0):
    """Minute ranges where HR cannot match the power (strap artefacts). Each rule (min_w, dur_s, end_hr, drop_bpm): a window of dur_s with
    power held in every third (>= 0.8 x min_w) and mean >= min_w, whose HR at the end (last 10 s) is below end_hr, or (if drop_bpm) falls
    by more than drop_bpm across it. Genuine efforts start low because HR lags, but rise (to 155-170 for Pat). Defaults: >= 200 W for 45 s
    (end < 145 or falling > 5), >= 150 W for 2 min (end < 135); the first skip_min minutes are ignored (HR still rising from rest, dry
    strap). tl = load_activity(path)[2]. Returns [(from_min, to_min, n_windows)].
    Found: 5 Sep min 22-29 (HR 75-130 at 180 W), 10 Sep min 40-58, 17 Oct (four stretches), 29 Sep min 56-57."""
    P = np.nan_to_num(tl["P"]); H = np.asarray(tl["H"], float); hits = []
    for min_w, dur, end_hr, drop_bpm in rules:
        c = np.convolve(P, np.ones(dur) / dur, "valid")
        for i in np.where(c >= min_w)[0][::5]:
            if i < skip_min * 60: continue
            h = H[i:i + dur]; q = P[i:i + dur]
            if np.isfinite(h).mean() < 0.6 or not np.isfinite(h[-10:]).any() or not np.isfinite(h[:10]).any(): continue
            if min(q[:dur // 3].mean(), q[dur // 3:2 * dur // 3].mean(), q[2 * dur // 3:].mean()) < 0.8 * min_w: continue   # power held throughout
            a, b = np.nanmean(h[:10]), np.nanmean(h[-10:])
            if b < end_hr or (drop_bpm is not None and a - b > drop_bpm): hits.append((i / 60, (i + dur) / 60))
    out = []
    for s, e in sorted(hits):
        if out and s - out[-1][1] <= merge_min: out[-1] = (out[-1][0], max(out[-1][1], e), out[-1][2] + 1)
        else: out.append((s, e, 1))
    return [(round(a, 1), round(b, 1), n) for a, b, n in out]


def hr_gaps(tl, min_s=30):
    """Stretches of riding (power or speed present) with missing or zero HR (strap lost) of at least min_s seconds (short gaps inside a
    stretch end it): [(from_min, to_min)]. Strava draws missing HR as a flat line (10 Sep km 7.3-14)."""
    H = np.asarray(tl["H"], float); mv = (np.nan_to_num(tl["P"]) > 0) | (np.nan_to_num(tl["S"]) > 1.0)    # riding, not paused
    bad = (~np.isfinite(H) | (H <= 0)) & mv; out = []; i = 0
    while i < len(H):
        if bad[i]:
            j = i
            while j + 1 < len(H) and bad[j + 1]: j += 1
            if j - i + 1 >= min_s: out.append((round(i / 60, 1), round((j + 1) / 60, 1)))
            i = j + 1
        else: i += 1
    return out


def hr_power_windows(tl, win_s=300, hr_last_s=120, skip_s=900, max_cv=0.45, min_speed=1.5, bad=None):
    """Quasi-steady windows of one ride for HR-zone work: every 60 s a `win_s` window (after the first `skip_s`), moving throughout,
    10-s power CV <= max_cv; HR = mean of its last `hr_last_s` s (HR lag). bad = [(from_min, to_min)] to blank (strap artefacts).
    Returns an array of (power, HR) rows."""
    P = np.nan_to_num(tl["P"]); H = np.asarray(tl["H"], float).copy(); S = np.nan_to_num(tl["S"]); out = []
    for a, b in (bad or []): H[int(a * 60):int(b * 60)] = np.nan
    for e in range(skip_s, len(P), 60):
        s = e - win_s; p = P[s:e]; h = H[e - hr_last_s:e]
        if s < 0 or (S[s:e] < min_speed).mean() > 0.05 or np.isfinite(h).mean() < 0.9: continue
        q = p[:win_s // 10 * 10].reshape(-1, 10).mean(1)
        if q.mean() <= 0 or q.std() / q.mean() > max_cv: continue
        hv = np.nanmean(h)
        if hv < 110 and p.mean() > 150: continue
        out.append((p.mean(), hv))
    return np.array(out)


def hr_zone_score(win, edges, ftp, pz=(0.55, 0.75, 0.90, 1.05)):
    """How well 5 HR zones (upper edges, e.g. [133, 148, 162, 173]: Z1 < 133 ...) reproduce the power zone (Coggan 5-zone fractions
    of ftp) of each window. Returns dict(balanced, exact, recall per power zone 2-5). Balanced = mean recall, so the big Z3 share
    does not dominate. 7 Nov: Pat's old set 44%, data-fitted set 63%."""
    z = np.digitize(win[:, 0], [f * ftp for f in pz]) + 1; hz = np.digitize(win[:, 1], edges) + 1
    rec = {k: float((hz[z == k] == k).mean()) for k in (2, 3, 4, 5) if (z == k).sum() >= 10}
    return dict(balanced=float(np.mean(list(rec.values()))) if rec else np.nan, exact=float((hz == z).mean()), recall=rec)


def hr_zone_optimise(win, ftp, z1=133, grid=((140, 152), (152, 166), (166, 182))):
    """Grid search of the Z2/Z3, Z3/Z4 and Z4/Z5 HR edges (Z1 edge fixed: few steady recovery windows) maximising hr_zone_score's
    balanced accuracy. 7 Nov (21 rides, 967 windows, FTP 175-185): 147 / 162 / 172; bootstrap by ride 145-149 / 156-164 / 172-174."""
    best = (-1, None)
    for a in range(*grid[0]):
        for b in range(*grid[1]):
            for c in range(*grid[2]):
                s = hr_zone_score(win, [z1, a, b, c], ftp)["balanced"]
                if s > best[0]: best = (s, [z1, a, b, c])
    return dict(edges=best[1], balanced=best[0])


def _series_1hz(s):
    """fit_series dict -> (t0, P, H, C) on a 1 Hz grid of elapsed seconds; gaps (pauses) are 0 W and NaN HR/cadence."""
    t0 = int(np.floor(np.nanmin(s["t"]))); n = int(np.ceil(np.nanmax(s["t"]))) - t0 + 1; k = (np.asarray(s["t"]) - t0).astype(int)
    P = np.zeros(n); H = np.full(n, np.nan); C = np.full(n, np.nan)
    P[k] = np.nan_to_num(s["p"]); H[k] = s["hr"]; C[k] = s["cad"] if "cad" in s and len(s["cad"]) else np.nan
    return t0, P, H, C


def hour_test_report(path, other=None, dur=3600, block_s=300, lthr_last_s=1200, show=True):
    """Analyse a long all-out test (default the 60-min FTP test) from one FIT (e.g. Edge/Stages), optionally a second recording of the same
    ride (`other`, e.g. the MyWhoosh/KICKR FIT): best `dur` window (elapsed: pauses count as 0 W), per-block W / HR / cadence, halves,
    pacing CV of 1-min means, Pw:HR decoupling, HR drift, LTHR estimate = average HR of the last `lthr_last_s` seconds (Friel), NP;
    with `other`: its average over the same (HR-aligned) window and the meter_offset table. Returns a dict."""
    s = fit_series(path); t0, P, H, C = _series_1hz(s)
    if len(P) < dur: raise ValueError("file shorter than %d s" % dur)
    c = np.convolve(P, np.ones(dur) / dur, "valid"); i = int(np.argmax(c)); w = slice(i, i + dur)
    p, h, cd = P[w], H[w], C[w]; half = dur // 2; m1 = p[:dur // 60 * 60].reshape(-1, 60).mean(1)
    blocks = [dict(start_min=k / 60, w=float(p[k:k + block_s].mean()), hr=float(np.nanmean(h[k:k + block_s])), hr_end=float(np.nanmean(h[k + block_s - 30:k + block_s])),
                   cad=float(np.nanmean(cd[k:k + block_s][cd[k:k + block_s] > 0])) if (cd[k:k + block_s] > 0).any() else np.nan) for k in range(0, dur, block_s)]
    w1, w2 = p[:half].mean(), p[half:].mean(); h1, h2 = np.nanmean(h[:half]), np.nanmean(h[half:])
    at = _at(); res = dict(start_min=i / 60, avg_w=float(p.mean()), np_w=float(at.norm_power(p)), cv_1min=float(m1.std() / m1.mean()),
               w_halves=(float(w1), float(w2)), hr_halves=(float(h1), float(h2)), decoupling_pct=float(((w1 / h1) / (w2 / h2) - 1) * 100),
               hr_avg=float(np.nanmean(h)), hr_max=float(np.nanmax(h)), lthr_est=float(np.nanmean(h[-lthr_last_s:])), zero_s=int((p == 0).sum()),
               cad=float(np.nanmean(cd[cd > 0])) if (cd > 0).any() else np.nan, blocks=blocks)
    if other is not None:
        o = fit_series(other) if isinstance(other, str) else other
        mo = meter_offset(s, o, show=False); to, Po, Ho, Co = _series_1hz(o); a = int(t0 + i - mo["lag_s"] - to)
        if 0 <= a and a + dur <= len(Po): res["other_avg_w"] = float(Po[a:a + dur].mean()); res["other_zero_s"] = int((Po[a:a + dur] == 0).sum())
        res["meter"] = mo
    if show:
        print("best %d min from min %.1f: %.1f W (NP %.1f), 1-min CV %.1f%%, halves %.1f / %.1f W, HR %.1f / %.1f, decoupling %+.1f%%, zeros %d s" % (
            dur // 60, res["start_min"], res["avg_w"], res["np_w"], res["cv_1min"] * 100, w1, w2, h1, h2, res["decoupling_pct"], res["zero_s"]))
        print("HR avg %.1f, max %.0f, last %d min %.1f (LTHR estimate), cadence %.0f" % (res["hr_avg"], res["hr_max"], lthr_last_s // 60, res["lthr_est"], res["cad"]))
        for b in blocks: print("  %4.0f min  %5.1f W  HR %5.1f (end %5.1f)  cad %4.0f" % (b["start_min"], b["w"], b["hr"], b["hr_end"], b["cad"]))
        if "other_avg_w" in res: print("other recording, same window: %.1f W (ratio %.3f); offset fit other = %.3f x ref %+.1f W" % (
            res["other_avg_w"], res["other_avg_w"] / res["avg_w"], res["meter"]["fit"][0], res["meter"]["fit"][1]))
    return res


def aerobic_check(path, targets=(130, 150), tol=10.0, min_s=(1200, 600), last_s=(600, 300), lag_s=180, other=None, show=True):
    """Aerobic check (progress check for goal a, every second week): 20 min at 130 W, then 10 min at 150 W, inside the Z2 part of a ride
    (KICKR, fan, usual room). `path` = FIT path or a fit_series()/stream_series() dict. For each target, finds the longest stretch whose
    30-s mean power stays within +-`tol` W of it; reports length, avg W, the HR of the last `last_s` seconds (the logged value), HR drift
    (first vs last third after `lag_s` s of HR lag), W/HR and cadence. With `other` (a second recording of the same ride, e.g. the Edge
    with the Stages) also the other meter's ratio on the same stretches (meter check). Returns a list of dicts (one per target)."""
    s = fit_series(path) if isinstance(path, str) else path; t0, P, H, C = _series_1hz(s)
    r30 = np.convolve(P, np.ones(30) / 30, "same"); out = []
    o = None
    if other is not None:
        o = fit_series(other) if isinstance(other, str) else other
        mo = meter_offset(s, o, show=False); to, Po, Ho, Co = _series_1hz(o)
    for k, tw in enumerate(targets):
        ok = (np.abs(r30 - tw) <= tol) & (P > 0); best = (0, 0); i = 0
        while i < len(ok):
            if ok[i]:
                j = i
                while j < len(ok) and ok[j]: j += 1
                if j - i > best[1] - best[0]: best = (i, j)
                i = j
            else: i += 1
        a, b = best; n = b - a; need = min_s[k] if k < len(min_s) else min_s[-1]; ls = last_s[k] if k < len(last_s) else last_s[-1]
        if n < 0.75 * need:
            out.append(dict(target_w=tw, found=False, length_s=int(n), need_s=int(0.75 * need))); continue
        h = H[a:b]; tail = slice(max(a, b - ls), b); hh = H[a + min(lag_s, n // 3):b]; third = max(1, len(hh) // 3)
        res = dict(target_w=tw, found=True, start_min=a / 60, length_s=int(n), avg_w=float(P[a:b].mean()), w_last=float(P[tail].mean()),
                   hr_last=float(np.nanmean(H[tail])), hr_avg=float(np.nanmean(h)), hr_drift=float(np.nanmean(hh[-third:]) - np.nanmean(hh[:third])),
                   cad=float(np.nanmean(C[a:b][C[a:b] > 0])) if (C[a:b] > 0).any() else np.nan, short=bool(n < 0.95 * need))
        res["w_per_hr"] = res["w_last"] / res["hr_last"] if res["hr_last"] > 0 else np.nan
        if o is not None:
            x = int(t0 + a - mo["lag_s"] - to); y = x + n
            if 0 <= x and y <= len(Po): res["other_w"] = float(Po[x:y].mean()); res["other_ratio"] = res["other_w"] / res["avg_w"]
        out.append(res)
    if show:
        for r in out:
            if not r["found"]: print("%d W: no stretch of at least %d s found (longest %d s)" % (r["target_w"], r["need_s"], r["length_s"])); continue
            print("%d W: from min %.1f, %.1f min, avg %.1f W, last part %.1f W at HR %.1f (W/HR %.3f), drift %+.1f bpm, cadence %.0f%s%s" % (
                r["target_w"], r["start_min"], r["length_s"] / 60, r["avg_w"], r["w_last"], r["hr_last"], r["w_per_hr"], r["hr_drift"], r["cad"],
                " (shorter than planned)" if r["short"] else "", ", other meter %.1f W (ratio %.3f)" % (r["other_w"], r["other_ratio"]) if "other_w" in r else ""))
    return out


def fourdp_report(path, show=True):
    """Analyse a 4DP / Full Frontal file (two 5-s sprints, 5 min, 20 min, 1 min, in that order) without laps or manual input.

    Finds the 5-min block as the best 5-min window, the 20 min as the best 20-min window after it, the 1 min as the best minute after the 20 min and
    the sprints as the two best 5-s windows before the 5 min. Blocks are best windows, as in Strava's best efforts, so they can start a few seconds
    away from the lap button (1 Nov: the best 20 min started 28 s after the lap press). Returns sprints, blocks (per-minute power / HR, CV, grade, km, speed), gaps between
    blocks (with stopped time) and strap quality; FTP by the 4DP rule = 100% of the 20-min average."""
    a, ex, tl = load_activity(path); P = np.nan_to_num(tl["P"])
    five = top_windows(P, 300, 1)[0][0]
    twenty = top_windows(P, 1200, 1, lo=five + 300)[0][0]
    one = top_windows(P, 60, 1, lo=twenty + 1200)[0][0]
    spr = sorted(top_windows(P, 5, 2, sep_s=30, hi=five), key=lambda x: x[0])
    sprints = []
    for s, w in spr:
        ss = s
        while ss > 0 and P[ss - 1] > 150: ss -= 1          # include the acceleration before the best 5 s
        w0 = max(0, ss - 2)                                  # the speed sensor lags power by 1-2 s
        sp = np.nan_to_num(tl["S"][s:s + 16]); w1 = s + int(np.argmax(sp)) + 2
        sprints.append(dict(start_s=int(s), best5s_w=w, peak_w=float(P[s:s + 5].max()), cad=float(np.nanmean(tl["C"][s:s + 5])),
                            speed_from_kmh=float(np.nan_to_num(tl["S"][w0]) * 3.6), speed_to_kmh=float(sp.max() * 3.6),
                            energy=sprint_energy_check(tl, w0, w1)))
    blocks = {"5min": _block(tl, five, 300), "20min": _block(tl, twenty, 1200), "1min": _block(tl, one, 60, per=10)}
    gaps = {"5min->20min": _gap(tl, five + 300, twenty), "20min->1min": _gap(tl, twenty + 1200, one)}
    strap = None
    try:
        df, s = hrv_quality(path); strap = dict(summary=s, flagged_minutes=[float(x) for x in df.loc[df.flag, "start_min"]])
    except Exception:
        pass
    res = dict(sprints=sprints, blocks=blocks, gaps=gaps, strap=strap, ftp_4dp=blocks["20min"]["avg_w"])
    if show:
        for i, s in enumerate(sprints, 1):
            print("sprint %d at %s: best 5 s %.0f W (peak %.0f), cadence %.0f, %.0f -> %.0f km/h, meter/physics %.2f" % (
                i, fmt_t(s["start_s"]), s["best5s_w"], s["peak_w"], s["cad"], s["speed_from_kmh"], s["speed_to_kmh"], s["energy"]["ratio"]))
        for k, b in blocks.items():
            print("%-5s at %s: %.1f W (NP %.0f, max %.0f), HR %.0f (first min %.0f, last min %.0f, max %.0f), cad %.0f, km %.2f-%.2f, %.1f km/h%s%s" % (
                k, fmt_t(b["start_s"]), b["avg_w"], b["np_w"], b["max_w"], b["hr_avg"], b["hr_first_min"], b["hr_last_min"], b["hr_max"], b["cad"], b["km_from"], b["km_to"],
                b["speed_kmh"], (", grade %+.2f%%" % b["grade_pct"]) if "grade_pct" in b else "", (", CV of minutes %.1f%%" % b["cv_pct"]) if "cv_pct" in b else ""))
            print("      W per %s: %s" % ("10 s" if k == "1min" else "minute", b["profile_w"]))
        for k, g in gaps.items():
            print("gap %s: %s (stopped %s), %.0f W while recording, %d s at 150-200 W, %d s above 200 W" % (k, fmt_t(g["seconds"]), fmt_t(g["stopped_s"]), g["avg_w_recorded"], g["s_150_200w"], g["s_over_200w"]))
        if strap: print("strap: %s; flagged minutes %s" % (strap["summary"], strap["flagged_minutes"]))
        print("FTP by the 4DP rule (100%% of the 20 min): %.0f W" % res["ftp_4dp"])
    return res


# ----------------------------------------------------------------------------- CSV / DIGEST
LABS = ["5s", "15s", "30s", "1min", "2min", "3min", "5min", "8min", "10min", "15min", "20min", "30min", "45min", "60min", "90min", "120min", "150min"]


def load_activities_csv(path, tz=None):
    """Strava export activities.csv -> clean DataFrame (pandas renames the duplicate headers 'Elapsed Time.1', 'Distance.1', 'Max Heart Rate.1', 'Relative Effort.1';
    the .1 versions are the numeric ones in seconds / metres). Timestamps in the CSV are UTC; start_local / date / week (Monday) are Europe/Berlin.
    Columns: id, start_utc, start_local, date, week, name, type, desc, elapsed_s, moving_s, km, gain_m, max_hr, avg_hr, max_w, avg_w (estimated before a power meter),
    wap, cad, rpe, rel_effort, gear, steps, file."""
    import pandas as pd
    tz = tz or CFG["tz"]; raw = pd.read_csv(path)

    def col(name, second=False):
        if second and name + ".1" in raw: return raw[name + ".1"]
        return raw[name] if name in raw else pd.Series(np.nan, index=raw.index)
    start = pd.to_datetime(raw["Activity Date"], format="%b %d, %Y, %I:%M:%S %p")
    df = pd.DataFrame({"id": raw.iloc[:, 0], "start_utc": start, "name": col("Activity Name"), "type": col("Activity Type"), "desc": col("Activity Description"),
                       "elapsed_s": col("Elapsed Time", True), "moving_s": col("Moving Time"), "km": col("Distance", True) / 1000.0, "gain_m": col("Elevation Gain"),
                       "max_hr": col("Max Heart Rate", True), "avg_hr": col("Average Heart Rate"), "max_w": col("Max Watts"), "avg_w": col("Average Watts"),
                       "wap": col("Weighted Average Power"), "cad": col("Average Cadence"), "rpe": col("Perceived Exertion"), "rel_effort": col("Relative Effort", True),
                       "gear": col("Activity Gear"), "steps": col("Total Steps"), "file": col("Filename")})
    df["start_local"] = df["start_utc"].dt.tz_localize("UTC").dt.tz_convert(tz)
    df["date"] = df["start_local"].dt.strftime("%Y-%m-%d")
    df["week"] = df["start_local"].dt.tz_localize(None).dt.to_period("W-SUN").apply(lambda x: x.start_time.date())
    return df.sort_values("start_utc").reset_index(drop=True)


def csv_totals(df):
    """Counts, km and hours by activity type, and km by gear (use to cross-check against Strava: connector gear totals, profile counts)."""
    out = {}
    for typ, g in df.groupby("type"): out[typ] = dict(n=int(len(g)), km=round(float(g.km.sum()), 1), hours=round(float(g.moving_s.sum() / 3600), 1))
    out["gear_km"] = {k: round(float(v), 1) for k, v in df.groupby("gear").km.sum().items()}
    return out


def parse_bests(text):
    """Parse current Strava all-time bests typed in by hand, e.g. "5s=686@2026-11-01, 20min=184@2026-11-01", into {'5s': (686.0, '2026-11-01'), ...}."""
    out = {}
    for item in re.split(r"[,;]\s*", text.strip()):
        m = re.match(r"(\w+)=([\d.]+)(?:@([\d-]+))?", item.strip())
        if m: out[m.group(1)] = (float(m.group(2)), m.group(3))
    return out


def _d(s):
    return datetime.strptime(str(s)[:10], "%Y-%m-%d").strftime("%d %b")


def bests_table_md(r, strava_now=None):
    """Markdown rows of the all-time bests table from the rides digest DataFrame (columns el_<dur>, ro_<dur>, date). With strava_now (see parse_bests) a
    'Strava all-time now' column is added; values that beat the archive (set after it) are bold."""
    import pandas as pd
    L = ["| Duration | Elapsed-based (archive) | Date | Strava all-time now | Date | Rolling (stops excl., archive) | Date |" if strava_now else
         "| Duration | Elapsed-based | Date | Rolling (stops excl.) | Date |", "|---|---|---|---|---|---|---|" if strava_now else "|---|---|---|---|---|"]
    for l in LABS:
        e = r["el_" + l].max() if "el_" + l in r else np.nan; ro = r["ro_" + l].max() if "ro_" + l in r else np.nan
        sn = (strava_now or {}).get(l)
        if not np.isfinite(e) and not np.isfinite(ro) and not sn: continue
        de = _d(r.loc[r["el_" + l].idxmax(), "date"]) if np.isfinite(e) else "-"; dr = _d(r.loc[r["ro_" + l].idxmax(), "date"]) if np.isfinite(ro) else "-"
        ev = "%.0f" % e if np.isfinite(e) else "-"; rv = "%.0f" % ro if np.isfinite(ro) else "-"
        if strava_now:
            if sn: sv = ("**%.0f**" % sn[0]) if (not np.isfinite(e) or sn[0] > round(e) + 0.5) else "%.0f" % sn[0]; sd = _d(sn[1]) if sn[1] else "-"
            else: sv, sd = "n/a", "-"
            L.append("| %s | %s | %s | %s | %s | %s | %s |" % (l, ev, de, sv, sd, rv, dr))
        else: L.append("| %s | %s | %s | %s | %s |" % (l, ev, de, rv, dr))
    return L


def monthly_bests_md(r, extra=None):
    """Bests by month (elapsed-based) for 5s, 1min, 5min, 10min, 20min and 60min.

    `extra` (e.g. {'2026-11': {'5s': 686}}) merges Strava bests set after the archive, marked *; months that only exist in `extra` get their own row."""
    cols = ["5s", "1min", "5min", "10min", "20min", "60min"]; r = r[r.np_w.notna()].copy(); r["m"] = r["date"].astype(str).str[:7]
    L = ["| Month | 5s | 1min | 5min | 10min | 20min | 60min |", "|---|---|---|---|---|---|---|"]
    groups = dict(tuple(r.groupby("m")))
    for m in sorted(set(groups) | set(extra or {})):
        g = groups.get(m); cells = []
        for l in cols:
            v = g["el_" + l].max() if g is not None and g["el_" + l].notna().any() else np.nan; x = (extra or {}).get(m, {}).get(l)
            cells.append(("%.0f*" % x) if x and (not np.isfinite(v) or x > v) else ("%.0f" % v if np.isfinite(v) else "-"))
        L.append("| %s | %s |" % (m, " | ".join(cells)))
    return L


def weekly_table_md(r, ftp=None):
    """Weekly load/intensity rows from the rides digest: rides (V = virtual/indoor), km, moving h, TSS-like, Z1-2 / Z3 / Z4+ shares
    (Z1-2 < 75%, Z3 75-90%, Z4+ >= 90% of the FTP used in the batch)."""
    p = r[r.np_w.notna()].copy(); p["wk"] = p["date"].astype(str).map(lambda s: datetime.strptime(s[:10], "%Y-%m-%d").date()).map(lambda d: d - __import__("datetime").timedelta(days=d.weekday()))
    virt = p["type"].astype(str).str.contains("Virtual") if "type" in p else p["date"].map(lambda x: False)
    L = ["| Week of | Rides (V = indoor) | km | Moving h | TSS-like | Z1-2 % | Z3 % | Z4+ % |", "|---|---|---|---|---|---|---|---|"]
    for wk, g in p.groupby("wk"):
        z = g[["z%d_min" % i for i in range(1, 8)]].sum(); t = z.sum(); nv = int(virt[g.index].sum())
        L.append("| %s | %d%s | %.0f | %.1f | %.0f | %.0f | %.0f | %.0f |" % (wk, len(g), " (%d V)" % nv if nv else "", g.dist_km.sum(), g.moving_s.sum() / 3600, g.tss_like.sum(),
                 (z.iloc[0] + z.iloc[1]) / t * 100, z.iloc[2] / t * 100, z.iloc[3:].sum() / t * 100))
    return L


def make_history_digest(rides_csv, runs_csv, out_md, strava_now=None, strava_virtual=None, extra_monthly=None, ftp=180, asof="", export_name="",
                        hr_notes=None, run_notes=None, after_archive_md=None, source_note="",
                        virtual_note="Indoor sessions so far without a strong fan (HR inflated)."):
    """Write history_digest.md from digest_rides.csv / digest_runs.csv (made by `analysis_tools.py --batch --ftp <ftp>`).

    Outdoor rides (Stages) and virtual rides (MyWhoosh, KICKR) are kept apart: the bests tables use outdoor rides; indoor bests get their own
    table (`strava_virtual` = parse_bests of the VirtualRide bests). `strava_now` (Ride bests from the connector) is shown next to the archive
    values (bold = set after the export). `hr_notes` {date: note} marks rides with unusable HR. `after_archive_md` (markdown lines) becomes
    section 8 for activities newer than the export. Run it at each refresh with the newest export."""
    import pandas as pd
    ra = pd.read_csv(rides_csv); ra["date"] = pd.to_datetime(ra["date"]).dt.strftime("%Y-%m-%d"); u = pd.read_csv(runs_csv)
    virt = ra["type"].astype(str).str.contains("Virtual") if "type" in ra else pd.Series(False, index=ra.index)
    r = ra[~virt].copy(); v = ra[virt].copy(); p = ra[ra.np_w.notna()]; po = r[r.np_w.notna()]
    z = p[["z%d_min" % i for i in range(1, 8)]].sum(); t = z.sum(); wcap = (p.pct_le_cap * p.recorded_s).sum() / p.recorded_s.sum()
    last = max(ra["date"].max(), str(u["date"].max()) if len(u) else ""); first_pw = po["date"].min() if len(po) else "-"
    hr_notes = hr_notes or {}
    nop = sorted(r[r.np_w.isna()]["date"]); nop_txt = ""
    if nop:  # group consecutive no-power dates into ranges (gaps <= 4 days)
        grp = [[nop[0], nop[0]]]
        for d in nop[1:]:
            if (pd.Timestamp(d) - pd.Timestamp(grp[-1][1])).days <= 4: grp[-1][1] = d
            else: grp.append([d, d])
        nop_txt = "; without power: " + ", ".join(_d(a) if a == b else "%s-%s" % (_d(a), _d(b)) for a, b in grp)
    L = ["# History digest: Pat, cycling | running\n",
         "As of: %s; activities to %s%s.\n" % (export_name or "Strava export", _d(last), "; tables updated " + asof if asof else ""),
         "Source: %s analysed with analysis_tools.py v2 and cp_lib.make_history_digest. Outdoor rides: %d (%d with power, from %s%s). Virtual rides (MyWhoosh, KICKR power): %d. Runs: %d. FTP for zones: %d W (working value, Stages scale). %s\n"
         % (export_name or "the Strava export", len(r), len(po), _d(first_pw), nop_txt, len(v), len(u), ftp, source_note),
         "## 1. Method and validation\n",
         "- **elapsed-based** = Strava power-curve convention (paused/stopped seconds count as 0 W). **rolling** = only recorded seconds with speed >= 1.0 m/s, coasting (0 W) kept; this matches Strava's 'average power' convention (stops excluded, coasting included).",
         "- Validation: the elapsed-based bests of the outdoor rides reproduce Strava's all-time Ride power curve (table 2), and the rolling 60-min value on 22 Sep (170.0 W) equals the 170 W average of that 59:54 ride. NP/avg of the 20 Sep ride also match (avg 149 W, NP 156 W).",
         "- Two power meters: outdoor rides use the Stages (left-only), virtual rides the KICKR (about +5 W at Z2 power, about equal at threshold power and normal cadence, about +8% below 60 rpm). Outdoor and indoor bests are therefore kept apart (Strava does the same: Ride vs VirtualRide).",
         "- HR: judge max HR by the 30-s mean (column in brackets); rides with unusable HR stretches are marked in table 5 (see section 7).\n",
         "## 2. All-time bests, outdoor rides (Stages, W)\n"]
    bt = bests_table_md(r, strava_now); L += bt + [
         "\nNotes: the 180-min elapsed value is a stop-heavy artefact and not reported. The rolling 20/30-min values of 16 Sep include short stops inside the window, so they overstate a continuous effort slightly." +
         (" Bold values in the 'Strava all-time now' column were set after this export." if any("**" in x for x in bt) else
          (" No Strava best is newer than this export." if strava_now else "")) + "\n"]
    if len(v):
        L += ["### Indoor bests (virtual rides, KICKR, W)\n", "| Duration | Elapsed-based | Date | Strava VirtualRide now |", "|---|---|---|---|"]
        prev = None; inv = []
        for l in LABS:
            if "el_" + l not in v or not v["el_" + l].notna().any(): continue
            e = v["el_" + l].max(); dd = v.loc[v["el_" + l].idxmax(), "date"]; sv = (strava_virtual or {}).get(l)
            L.append("| %s | %.0f | %s | %s |" % (l, e, _d(dd), ("%.0f (%s)" % (sv[0], _d(sv[1]))) if sv else "n/a"))
            if prev and round(e) > round(prev[1]): inv.append("%s: %s %.0f W > %s %.0f W" % (_d(dd), l, e, prev[0], prev[1]))
            prev = (l, e)
        note = "\n" + (virtual_note + " " if virtual_note else "")
        if inv:
            note += ("Where a longer duration shows a higher value than a shorter one (%s), it is genuine, not an error: a window with harder "
                     "stretches at both ends can average more than any shorter window inside it." % "; ".join(inv))
        L.append(note.rstrip() + "\n")
    L += ["## 3. Bests by month, outdoor rides (elapsed-based, W)\n"] + monthly_bests_md(r, extra_monthly) + ["" if not extra_monthly else "\n* = Strava best effort after the export.\n",
         "## 4. Weekly load and intensity (all rides with power, FTP %d W)\n" % ftp,
         "Z1-2 = below 75%% FTP (< %d W), Z3 = 75-90%% (%d-%d W), Z4+ = 90%% FTP and above (>= %d W). TSS-like = duration x IF^2 x 100 from NP. Indoor sessions (V) are KICKR power.\n" % (round(0.75 * ftp), round(0.75 * ftp), round(0.90 * ftp), round(0.90 * ftp))] + weekly_table_md(ra) + [
         "\nAll power rides: Z1-2 %.0f%%, Z3 %.0f%%, Z4+ %.0f%% of pedalled time; %.0f%% of time at or below the 135 W easy cap. Reading (my view): most riding so far was tempo and above; the plan's base work needs a deliberately larger Z1-2 share.\n"
         % ((z.iloc[0] + z.iloc[1]) / t * 100, z.iloc[2] / t * 100, z.iloc[3:].sum() / t * 100, wcap),
         "## 5. Per ride (rides with power; V = indoor, KICKR)\n", "| Date | | km | Moving min | Avg W (moving) | NP | IF | % time <=135 W | HR avg/max (30 s max) | Cadence |", "|---|---|---|---|---|---|---|---|---|---|"]
    for _, x in p.sort_values("date").iterrows():
        hr = "-" if pd.isna(x.hr_avg) else "%.0f/%.0f (%.0f)" % (x.hr_avg, x.hr_max, x.hr_max30)
        if x.date in hr_notes: hr += " %s" % hr_notes[x.date]
        L.append("| %s | %s | %.1f | %.0f | %.0f | %.0f | %.2f | %.0f | %s | %.0f |" % (x.date, "V" if "Virtual" in str(x.get("type", "")) else "", x.dist_km, x.moving_s / 60, x.avg_w_moving, x.np_w, x.if_, x.pct_le_cap, hr, x.cad_mean))
    L += ["\n## 6. Runs\n", "| Date | Name | km | Moving | Pace | HR avg/max | Splits per km (moving time) | Best 1K / mile / 5K (windowed) |", "|---|---|---|---|---|---|---|---|"]
    at = _at(); bf = lambda val: fmt_t(val) if pd.notna(val) else "-"
    for _, x in u.sort_values("date").iterrows():
        L.append("| %s | %s | %.2f | %s | %s | %.0f/%.0f | %s | %s / %s / %s |" % (x.date, x["name"], x.dist_km, fmt_t(x.moving_s), at.fmt_pace(x.pace_moving), x.hr_avg, x.hr_max, x.splits_km if isinstance(x.splits_km, str) else "-", bf(x.best_1k), bf(x.best_mile), bf(x.best_5k)))
    L += ["\nCaveats: GPX-based run rows use raw GPS distance and a simple pause rule. " + (run_notes or "") + "\n",
          "## 7. Other data notes\n",
          "- Avg watts in Strava's activities.csv for the rides 7-20 Aug (and the MTB laps) are Strava estimates, not measured; the files contain no power. First measured power: 29 Aug.",
          "- The Garmin files also contain beat-to-beat (HRV) messages; cp_lib.hrv_quality() uses them to check HR strap artefacts; cp_lib.hr_artefact_scan() / hr_gaps() find stretches where HR cannot match the power or is missing.",
          "- Strava-made run FIT files: the 'speed' field runs far slower than distance-derived speed; use the distance field for pacing."]
    if after_archive_md:
        L += ["\n## 8. After the export\n"] + list(after_archive_md)
    open(out_md, "w", encoding="utf-8").write("\n".join(L) + "\n"); return len("\n".join(L))


# ----------------------------------------------------------------------------- INDEX
def _first_sentence(doc):
    """First sentence of a docstring, joined across wrapped lines (abbreviations such as 'e.g.' do not end it)."""
    para = " ".join(doc.strip().split("\n\n")[0].split())
    if not para: return ""
    safe = re.sub(r"\b(e\.g|i\.e|vs|approx|incl)\.", lambda m: m.group(0).replace(".", "\x00"), para)
    m = re.search(r"\.(\s|$)", safe)
    s = (safe[:m.start() + 1] if m else safe).replace("\x00", ".").strip()
    return s if s.endswith((".", ":", "?", "!")) else s + "."


def _md_code(text):
    """Put tag-like tokens such as el_<dur> into backticks (markdown would hide them as HTML); text already in backticks is left alone."""
    parts = re.split(r"(`[^`]*`)", text)
    for i, p in enumerate(parts):
        if not p.startswith("`"):
            parts[i] = re.sub(r"[\w.]*<[A-Za-z_]+>[\w.]*", lambda m: "`%s`" % m.group(0), p)
    return "".join(parts)


def index(md=False):
    """Print the function index of this module grouped by section (md=True: markdown for README.md)."""
    src = open(os.path.abspath(__file__), encoding="utf-8").read().split("\n"); sec = "(top)"; items = []
    for ln in src:
        m = re.match(r"^# -{20,} (.+)$", ln)
        if m: sec = m.group(1).strip()
        d = re.match(r"^(def|class) ([A-Za-z]\w*)", ln)
        if d and not d.group(2).startswith("_"): items.append((sec, d.group(2)))
    cur = None; me = globals()
    for sec, name in items:
        if sec != cur:
            print(("\n### " + sec.replace("analysis_tools.py", "`analysis_tools.py`")) if md else ("\n== " + sec)); cur = sec
        doc = _first_sentence(me[name].__doc__ or "")
        print(("- `%s`: %s" % (name, _md_code(doc))) if md else ("  %s\n      %s" % (name, doc)))


if __name__ == "__main__":
    import sys
    if "--index-md" in sys.argv: index(True)
    elif "--index" in sys.argv: index(False)
    else: print(__doc__)

#!/usr/bin/env python3
"""cp_lib.py (v1, 2026-11-01) - reusable helpers for the 'cycling | running' coaching project.

Companion to analysis_tools.py (activity files -> reports / digest) and routes_tool.py (GPX route geometry).
This module collects everything else that was written ad hoc during the chats:
  PHYSICS    power <-> speed <-> wind model, critical-power sketches
  SUN        sunrise / sunset (NOAA approximation, DST-aware)
  PATCH      safe text patcher for the markdown files (every edit asserts that its target exists)
  FIT        inspection of FIT files: structure, laps, timer events, pauses, HRV / strap quality
  RIDE       10-min block tables, best windows (power, HR, distance, speed), decoupling, HR by power, effort finder
  RUN        splits, halves, tail paces, fastest windows (reps), HR plateaus / steps / zone time, loop length
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
CFG = dict(ftp=175.0, z2cap=135.0, tz="Europe/Berlin", home=(50.8438, 6.8942), sun_site=(50.94, 6.96),
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
    Returns (DataFrame per window: start_min, beats, artefact_pct, hr_from_rr, flag), summary dict). RR time runs on cumulative RR, so it
    can drift a little against the record timeline. A loosening strap shows up as rising artefact_pct / missing beats."""
    import pandas as pd
    rr = []
    for m in _fitfile(path).get_messages("hrv"):
        rr.extend([x for x in (m.get_value("time") or ()) if x is not None])
    rr = np.array(rr, float)
    if len(rr) < 20: return pd.DataFrame(), {"beats": int(len(rr))}
    med = np.array([np.median(rr[max(0, i - 3):i + 4]) for i in range(len(rr))])
    bad = (np.abs(rr - med) > tol * med) | (rr < 0.3) | (rr > 2.0)
    tt = np.cumsum(rr); rows = []
    for k in range(int(tt[-1] // win_s) + 1):
        m = (tt >= k * win_s) & (tt < (k + 1) * win_s)
        if m.sum() == 0: continue
        pct = bad[m].mean() * 100
        rows.append(dict(start_min=k * win_s / 60, beats=int(m.sum()), artefact_pct=round(pct, 1), hr_from_rr=round(60 / np.mean(rr[m & ~bad]), 0) if (m & ~bad).any() else np.nan, flag=pct > flag_pct))
    df = pd.DataFrame(rows)
    return df, {"beats": int(len(rr)), "artefact_pct": round(bad.mean() * 100, 2), "flagged_windows": int(df["flag"].sum()), "windows": int(len(df))}


# ----------------------------------------------------------------------------- shared loading (uses analysis_tools.py)
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
    """'5s=544@2026-10-31, 15s=448@2026-10-30, 20min=175@2026-10-31' -> {'5s': (544.0, '2026-10-31'), ...} (current Strava all-time bests, typed in by hand)."""
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
    """Bests by month (elapsed-based) for 5s, 1min, 5min, 10min, 20min, 60min; extra={'2026-10': {'5s': 544}} merges later Strava bests (marked *)."""
    cols = ["5s", "1min", "5min", "10min", "20min", "60min"]; r = r[r.np_w.notna()].copy(); r["m"] = r["date"].astype(str).str[:7]
    L = ["| Month | 5s | 1min | 5min | 10min | 20min | 60min |", "|---|---|---|---|---|---|---|"]
    for m, g in r.groupby("m"):
        cells = []
        for l in cols:
            v = g["el_" + l].max() if g["el_" + l].notna().any() else np.nan; x = (extra or {}).get(m, {}).get(l)
            cells.append(("%.0f*" % x) if x and (not np.isfinite(v) or x > v) else ("%.0f" % v if np.isfinite(v) else "-"))
        L.append("| %s | %s |" % (m, " | ".join(cells)))
    return L


def weekly_table_md(r, ftp=None):
    """Weekly load/intensity rows from the rides digest: rides, km, moving h, TSS-like, Z1-2 / Z3 / Z4+ shares (Z4+ = >= 90% FTP)."""
    p = r[r.np_w.notna()].copy(); p["wk"] = p["date"].astype(str).map(lambda s: datetime.strptime(s[:10], "%Y-%m-%d").date()).map(lambda d: d - __import__("datetime").timedelta(days=d.weekday()))
    L = ["| Week of | Rides | km | Moving h | TSS-like | Z1-2 % | Z3 % | Z4+ % |", "|---|---|---|---|---|---|---|---|"]
    for wk, g in p.groupby("wk"):
        z = g[["z%d_min" % i for i in range(1, 8)]].sum(); t = z.sum()
        L.append("| %s | %d | %.0f | %.1f | %.0f | %.0f | %.0f | %.0f |" % (wk, len(g), g.dist_km.sum(), g.moving_s.sum() / 3600, g.tss_like.sum(), (z.iloc[0] + z.iloc[1]) / t * 100, z.iloc[2] / t * 100, z.iloc[3:].sum() / t * 100))
    return L


def make_history_digest(rides_csv, runs_csv, out_md, strava_now=None, extra_monthly=None, ftp=175, asof="", source_note=""):
    """Write history_digest.md from digest_rides.csv / digest_runs.csv (made by `analysis_tools.py --batch`). strava_now / extra_monthly add the bests
    set after the archive (see parse_bests). Run this at each weekly refresh so the tables, not extra text, carry the new bests."""
    import pandas as pd
    r = pd.read_csv(rides_csv); r["date"] = pd.to_datetime(r["date"]).dt.strftime("%Y-%m-%d"); u = pd.read_csv(runs_csv); p = r[r.np_w.notna()]
    z = p[["z%d_min" % i for i in range(1, 8)]].sum(); t = z.sum(); wcap = (p.pct_le_cap * p.recorded_s).sum() / p.recorded_s.sum()
    L = ["# History digest: Pat, cycling | running (archive to 26 Oct 2026, plus 28 Oct 5K)" + ("; tables updated " + asof if asof else "") + "\n",
         "Source: Strava archive (49 activity files to 26 Oct, 30_10.fit = 28 Oct 5K), analysed with analysis_tools.py v2. " + source_note +
         "Rides: 43 (30 with a power meter from 29 Aug; the rides 7-20 Aug, the 16 Aug gravel ride and the 26 Sep MTB lap have no power in the files). FTP for zones: %d W (working value).\n" % ftp,
         "## 1. Method and validation\n",
         "- **elapsed-based** = Strava power-curve convention (paused/stopped seconds count as 0 W). **rolling** = only recorded seconds with speed >= 1.0 m/s, coasting (0 W) kept; this matches Strava's 'average power' convention (stops excluded, coasting included).",
         "- Validation: the elapsed-based archive bests reproduce Strava's all-time power curve at every duration the connector offers, and the rolling 60-min value on 22 Sep (170.0 W) equals the 170 W average of that 59:54 ride. NP/avg of the 20 Sep ride also match (avg 149 W, NP 156 W).",
         "- Strava HR-flag counter in v1/v2 is capped at 8 and says nothing for 1 Hz ride files (steady HR repeats often); judge max HR by the 30-s mean instead (columns hr_max / hr_max30 in digest_rides.csv).\n",
         "## 2. All-time bests (W)\n"] + bests_table_md(r, strava_now) + [
         "\nNotes: 120 min elapsed 144 W matches the brief. The 180-min elapsed value (86 W) is a stop-heavy artefact and not reported. The rolling 20/30-min values (183/184 W, 16 Sep) include short stops inside the window, so they overstate a continuous effort slightly. "
         + ("Bold values in the 'Strava all-time now' column were set after the archive (30/31 Oct rides); the archive columns do not change, the rolling column is archive-only.\n" if strava_now else "\n"),
         "## 3. Bests by month (elapsed-based, W)\n"] + monthly_bests_md(r, extra_monthly) + ["" if not extra_monthly else "\n* = Strava best effort after the archive.\n",
         "## 4. Weekly load and intensity (rides with power, FTP %d W)\n" % ftp,
         "Z1-2 = below 75% FTP (< 131 W), Z3 = 75-90% (131-157 W), Z4+ = 90% FTP and above (>= 157 W). TSS-like = duration x IF^2 x 100 from NP.\n"] + weekly_table_md(r) + [
         "\nAll power rides: Z1-2 %.0f%%, Z3 %.0f%%, Z4+ %.0f%% of pedalled time; %.0f%% of time at or below the 135 W easy cap. Reading (my view): the riding so far was mostly tempo and above; the plan's base work needs a deliberately larger Z1-2 share.\n"
         % ((z.iloc[0] + z.iloc[1]) / t * 100, z.iloc[2] / t * 100, z.iloc[3:].sum() / t * 100, wcap),
         "## 5. Per ride (power rides)\n", "| Date | km | Moving min | Avg W (moving) | NP | IF | % time <=135 W | HR avg/max (30 s max) | Cadence |", "|---|---|---|---|---|---|---|---|---|"]
    for _, x in p.sort_values("date").iterrows():
        hr = "-" if pd.isna(x.hr_avg) else "%.0f/%.0f (%.0f)" % (x.hr_avg, x.hr_max, x.hr_max30)
        L.append("| %s | %.1f | %.0f | %.0f | %.0f | %.2f | %.0f | %s | %.0f |" % (x.date, x.dist_km, x.moving_s / 60, x.avg_w_moving, x.np_w, x.if_, x.pct_le_cap, hr, x.cad_mean))
    L += ["\n## 6. Runs\n", "| Date | Name | km | Moving | Pace | HR avg/max | Splits per km (moving time) | Best 1K / mile / 5K (windowed) |", "|---|---|---|---|---|---|---|---|"]
    at = _at(); bf = lambda v: fmt_t(v) if pd.notna(v) else "-"
    for _, x in u.sort_values("date").iterrows():
        L.append("| %s | %s | %.2f | %s | %s | %.0f/%.0f | %s | %s / %s / %s |" % (x.date, x["name"], x.dist_km, fmt_t(x.moving_s), at.fmt_pace(x.pace_moving), x.hr_avg, x.hr_max, x.splits_km if isinstance(x.splits_km, str) else "-", bf(x.best_1k), bf(x.best_mile), bf(x.best_5k)))
    L += ["\nCaveats: GPX-based run rows use raw GPS distance and a simple pause rule. 14 Oct: the script's best 1K (3:51) and mile (7:14) are faster than Strava's (4:01, 7:32) and its moving time (42:16) is longer than Strava's (39:06), so use Strava's numbers for that run. The 28 Oct row (FIT) uses Strava's recorded distance (5.000 km in 23:30) and matches Strava.\n",
          "## 7. Other data notes\n",
          "- Avg watts in Strava's activities.csv for the rides 7-20 Aug (and the MTB laps) are Strava estimates, not measured; the files contain no power. First measured power: 29 Aug.",
          "- The Garmin files also contain beat-to-beat (HRV) messages; cp_lib.hrv_quality() uses them to check HR strap artefacts.",
          "- In the 28 Oct FIT, the 'speed' field runs far slower than distance-derived speed (e.g. 5:20/km vs about 3:55/km at the finish): use the distance field for pacing."]
    open(out_md, "w", encoding="utf-8").write("\n".join(L)); return len("\n".join(L))


# ----------------------------------------------------------------------------- INDEX
def index(md=False):
    """Print the function index of this module grouped by section (md=True: markdown for README.md)."""
    import inspect
    src = open(os.path.abspath(__file__), encoding="utf-8").read().split("\n"); sec = "(top)"; items = []
    for ln in src:
        m = re.match(r"^# -{20,} (.+)$", ln)
        if m: sec = m.group(1).strip()
        d = re.match(r"^(def|class) ([A-Za-z]\w*)", ln)
        if d: items.append((sec, d.group(2)))
    cur = None; me = globals()
    for sec, name in items:
        if sec != cur: print(("\n### " if md else "\n== ") + sec); cur = sec
        doc = (me[name].__doc__ or "").strip().split("\n")[0]; sig = ""
        try: sig = str(inspect.signature(me[name]))
        except Exception: pass
        print(("- `%s%s`: %s" if md else "  %s%s\n      %s") % (name, sig, doc))


if __name__ == "__main__":
    import sys
    if "--index-md" in sys.argv: index(True)
    elif "--index" in sys.argv: index(False)
    else: print(__doc__)

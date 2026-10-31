#!/usr/bin/env python3
"""analysis_tools.py (v2) - quick analysis of Strava/Garmin GPX and FIT / FIT.GZ files.

Works for rides (with power) and runs (HR + pace).  Needs python3 + numpy; FIT files also need fitparse
(pip install fitparse --break-system-packages); --batch also needs pandas.

Usage examples
  python analysis_tools.py ride.gpx --ftp 175
  python analysis_tools.py run.gpx --lap 1265 --target 5000
Options
  --ftp N      FTP used for zones/IF (default 175)
  --z2cap N    easy-ride power cap in watts (default 135)
  --lap M      lap length in metres for run lap splits (default 1250)
  --target M   report elapsed time when this distance is reached (runs)
  --tz NAME    time zone for the start time (default Europe/Berlin)
  --stop-speed V  speed (m/s) below which a recorded second counts as stopped (default 1.0)
  --batch DIR  analyse every file listed in --csv (Strava activities.csv) found in DIR; writes --out files
  --csv FILE   Strava activities.csv (columns 'Filename', 'Activity Date', 'Activity Type')
  --out DIR    output folder for --batch (default digest)

What it prints (and flags)
  rides: time/distance, avg power (with and without zeros), NP, VI, IF/TSS-like,
         Coggan zone minutes, share above the easy cap, hard efforts, mean-max curve
         (stops/coasting counted as zeros, like Strava), cadence mix, HR by thirds
  runs : km and lap splits with HR, 2-min blocks, recording gaps/pauses, loop length,
         HR at pace table, time at target distance
  both : data-quality flags (HR flat-lines, sudden HR jumps, recording gaps)
"""
import re
import sys
import argparse
from datetime import datetime, timezone

import numpy as np

R_EARTH = 6371000.0


# ----------------------------------------------------------------------------- loading
def _num(block, tags):
    for t in tags:
        m = re.search(r"<%s>(-?[\d.]+)</%s>" % (t, t), block)
        if m:
            return float(m.group(1))
    return float("nan")


def load_gpx(path):
    txt = open(path, encoding="utf-8").read()
    pts = re.findall(r'<trkpt lat="(-?[\d.]+)" lon="(-?[\d.]+)">(.*?)</trkpt>', txt, re.S)
    rows = []
    for la, lo, b in pts:
        tm = re.search(r"<time>(.*?)</time>", b)
        if not tm:
            continue
        s = tm.group(1).replace("Z", "").split(".")[0]
        t = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
        rows.append((t, float(la), float(lo),
                     _num(b, ["ele"]),
                     _num(b, ["power", "gpxpx:PowerInWatts", "PowerInWatts"]),
                     _num(b, ["gpxtpx:hr", "hr"]),
                     _num(b, ["gpxtpx:cad", "cad"]),
                     _num(b, ["gpxtpx:atemp", "atemp"])))
    if not rows:
        raise SystemExit("no track points found in %s" % path)
    return np.array(rows)


def haversine(la1, lo1, la2, lo2):
    p1, p2 = np.radians(la1), np.radians(la2)
    dp, dl = p2 - p1, np.radians(lo2 - lo1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R_EARTH * np.arcsin(np.sqrt(a))


def fmt_t(sec):
    sec = int(round(sec))
    return "%d:%02d" % (sec // 60, sec % 60)


def fmt_pace(sec_per_km):
    if not np.isfinite(sec_per_km) or sec_per_km <= 0:
        return "-"
    return fmt_t(sec_per_km) + "/km"


# ----------------------------------------------------------------------------- helpers
def timeline(a, ex=None):
    """Resample to 1 Hz; missing seconds stay NaN; 'rec' marks recorded seconds."""
    t = a[:, 0].astype(int)
    n = t[-1] - t[0] + 1
    idx = t - t[0]
    out = {}
    for name, col in (("P", 4), ("H", 5), ("C", 6), ("T", 7), ("E", 3)):
        arr = np.full(n, np.nan)
        arr[idx] = a[:, col]
        out[name] = arr
    rec = np.zeros(n, bool)
    rec[idx] = True
    out["rec"] = rec
    for name, key in (("S", "speed"), ("D", "dist")):
        arr = np.full(n, np.nan)
        if ex and key in ex:
            arr[idx] = ex[key]
        out[name] = arr
    return out


def norm_power(x):
    if len(x) < 30:
        return float("nan")
    r = np.convolve(x, np.ones(30) / 30, mode="valid")
    return float(np.mean(r ** 4) ** 0.25)


def mean_max(x, d):
    if len(x) < d:
        return float("nan")
    cs = np.cumsum(np.insert(x, 0, 0.0))
    return float(((cs[d:] - cs[:-d]) / d).max())


def hr_quality(h):
    """Flag flat-lines (>=10 identical values) and sudden jumps (>=8 bpm in 10 s)."""
    hh = h[~np.isnan(h)]
    flags = []
    if len(hh) < 30:
        return flags
    run, start = 1, 0
    for i in range(1, len(hh)):
        if hh[i] == hh[i - 1]:
            run += 1
        else:
            if run >= 10:
                flags.append("HR flat-line: %d identical readings of %.0f bpm around minute %.1f" % (run, hh[i - 1], (i - run) / 60))
            run = 1
    if run >= 10:
        flags.append("HR flat-line at the end: %d identical readings of %.0f bpm" % (run, hh[-1]))
    last = -999
    for i in range(10, len(hh) - 10):
        ch = hh[i:i + 10].mean() - hh[i - 10:i].mean()
        if abs(ch) >= 8 and i - last > 60:
            flags.append("sudden HR step %+.0f bpm around minute %.1f" % (ch, i / 60))
            last = i
    return flags[:8]


# ----------------------------------------------------------------------------- rides
def ride_report(tl, a, ftp, z2cap):
    P, H, C, T, rec = tl["P"], tl["H"], tl["C"], tl["T"], tl["rec"]
    m = rec & ~np.isnan(P)
    p = P[m]
    hh = H[m]
    c = C[m]
    ps = np.convolve(p, np.ones(3) / 3, mode="same")
    npw = norm_power(p)
    print("Power: avg %.0f W incl. coasting zeros (%.0f W excl.), zeros %.1f%% (%.1f min), NP %.0f W, VI %.2f, max %.0f W"
          % (p.mean(), p[p > 0].mean(), (p == 0).mean() * 100, (p == 0).sum() / 60, npw, npw / p.mean(), p.max()))
    IF = npw / ftp
    print("At FTP %d W: IF %.2f, TSS-like %.0f, work %.0f kJ" % (ftp, IF, len(p) / 3600 * IF ** 2 * 100, p.sum() / 1000))
    edges = [0, .55, .75, .90, 1.05, 1.20, 1.50, 99]
    mins = [((ps / ftp >= edges[i]) & (ps / ftp < edges[i + 1])).sum() / 60 for i in range(7)]
    print("Zone minutes Z1..Z7: " + " ".join("Z%d %.1f" % (i + 1, v) for i, v in enumerate(mins)))
    print("Time at or below %d W: %.0f%%; above: %.0f%%" % (z2cap, (ps <= z2cap).mean() * 100, (ps > z2cap).mean() * 100))
    # hard efforts
    sm = np.convolve(p, np.ones(5) / 5, mode="same")
    runs, i = [], 0
    while i < len(sm):
        if sm[i] >= 1.2 * ftp:
            j = i
            while j < len(sm) and sm[j] >= 0.97 * ftp:
                j += 1
            if j - i >= 8:
                runs.append((i, j))
            i = j
        else:
            i += 1
    print("Hard efforts (>=%.0f W, held >=8 s): %d" % (1.2 * ftp, len(runs)))
    for i, j in runs[:12]:
        print("   min %5.1f: %3d s avg %3.0f W max %3.0f W" % (i / 60, j - i, p[i:j].mean(), p[i:j].max()))
    pz = np.where(rec, np.nan_to_num(P), 0.0)
    cs = np.cumsum(np.insert(pz, 0, 0.0))
    curve = []
    for d, lab in ((5, "5s"), (15, "15s"), (30, "30s"), (60, "1min"), (120, "2min"), (180, "3min"), (300, "5min"),
                   (600, "10min"), (1200, "20min"), (1800, "30min"), (3600, "60min")):
        if len(pz) > d:
            curve.append("%s %.0f" % (lab, ((cs[d:] - cs[:-d]) / d).max()))
    print("Mean-max (stops/coasting count as zero): " + ", ".join(curve))
    cp = c[(c > 0) & ~np.isnan(c)]
    if len(cp):
        print("Cadence (pedalling): mean %.0f; <70 %.0f%%, 70-84 %.0f%%, 85-95 %.0f%%, >95 %.0f%%"
              % (cp.mean(), (cp < 70).mean() * 100, ((cp >= 70) & (cp < 85)).mean() * 100,
                 ((cp >= 85) & (cp <= 95)).mean() * 100, (cp > 95).mean() * 100))
    ok = ~np.isnan(hh)
    if ok.sum() > 300:
        print("HR: avg %.0f, max %.0f" % (np.nanmean(hh), np.nanmax(hh)))
        k = len(p)
        for j in range(3):
            sl = slice(j * k // 3, (j + 1) * k // 3)
            pp, hq = p[sl], hh[sl]
            mk = (pp > 60) & ~np.isnan(hq)
            if mk.sum() > 30:
                print("   third %d: pedalling avg %.0f W, HR %.0f, W/HR %.2f" % (j + 1, pp[mk].mean(), hq[mk].mean(), pp[mk].mean() / hq[mk].mean()))
    t_ok = T[~np.isnan(T)]
    if len(t_ok):
        print("Temperature: mean %.1f C" % t_ok.mean())


# ----------------------------------------------------------------------------- runs
def run_report(tl, a, lap, target):
    t = a[:, 0]
    d = haversine(a[:-1, 1], a[:-1, 2], a[1:, 1], a[1:, 2])
    cum = np.concatenate([[0], np.cumsum(d)])
    if _EX.get("dist") is not None and np.isfinite(_EX["dist"]).all() and len(_EX["dist"]) == len(t):
        cum = np.asarray(_EX["dist"], float) - float(_EX["dist"][0])   # recorded (device/Strava) distance
        d = np.diff(cum)
    dt = np.diff(t)
    H = a[:, 5]
    tot = t[-1] - t[0]
    # moving-time axis: pauses (gap >2.5 s while moving <1 m/s) are removed, data loss while moving is kept
    stop = (dt > 2.5) & (d / np.maximum(dt, 1) < 1.0)
    mt = np.concatenate([[0], np.cumsum(np.where(stop, 0.0, dt))])
    tot_m = mt[-1]
    print("Distance %.3f km; elapsed %s (%s); moving %s (%s)"
          % (cum[-1] / 1000, fmt_t(tot), fmt_pace(tot / (cum[-1] / 1000)), fmt_t(tot_m), fmt_pace(tot_m / (cum[-1] / 1000))))
    gaps = np.where(dt > 2.5)[0]
    print("Recording gaps >2.5 s: %d (total %s)" % (len(gaps), fmt_t(dt[gaps].sum() if len(gaps) else 0)))
    for g in gaps[:6]:
        kind = "pause" if stop[g] else "data loss while moving"
        print("   gap at minute %.1f (km %.2f): %s, %.0f m moved across it (%s)" % ((t[g] - t[0]) / 60, cum[g] / 1000, fmt_t(dt[g]), d[g], kind))
    hv = H[~np.isnan(H)]
    if len(hv):
        print("HR: avg %.0f, max %.0f" % (hv.mean(), hv.max()))

    def at(dist):
        return float(np.interp(dist, cum, mt))

    nk = int(cum[-1] // 1000)
    print("Per km (moving time):")
    prev = 0.0
    for k in range(1, nk + 1):
        s = at(k * 1000)
        m = (cum >= (k - 1) * 1000) & (cum < k * 1000)
        print("   km %d: %s  HR %.0f (max %.0f)" % (k, fmt_t(s - prev), np.nanmean(H[m]) if m.any() else float("nan"),
                                                  np.nanmax(H[m]) if m.any() else float("nan")))
        prev = s
    rem = cum[-1] - nk * 1000
    if rem > 100:
        m = cum >= nk * 1000
        s = tot_m - prev
        print("   last %.2f km: %s (%s)  HR %.0f" % (rem / 1000, fmt_t(s), fmt_pace(s / (rem / 1000)), np.nanmean(H[m])))
    if lap and cum[-1] >= lap:
        print("Laps of %d m (moving time):" % lap)
        prev, n = 0.0, int(cum[-1] // lap)
        for k in range(1, n + 1):
            s = at(k * lap)
            m = (cum >= (k - 1) * lap) & (cum < k * lap)
            print("   lap %d: %s (%s)  HR %.0f" % (k, fmt_t(s - prev), fmt_pace((s - prev) / (lap / 1000)), np.nanmean(H[m])))
            prev = s
    print("2-minute blocks of moving time (pace / HR):")
    for i in range(0, int(tot_m) - 60, 120):
        m = (mt >= i) & (mt < i + 120)
        if m.sum() > 10:
            dd, tt = cum[m][-1] - cum[m][0], mt[m][-1] - mt[m][0]
            if dd > 20 and tt > 0:
                print("   %2d-%2d min: %s  HR %.0f" % (i // 60, (i + 120) // 60, fmt_pace(tt / (dd / 1000)), np.nanmean(H[m])))
    # HR at pace (30 s windows)
    sp = np.concatenate([[0], d / np.maximum(dt, 1)])
    sp[np.concatenate([[False], dt > 2.5])] = np.nan
    if len(sp) > 60:
        w = np.convolve(np.nan_to_num(sp), np.ones(30) / 30, mode="same")
        bins = [(0, 4.5 * 60, "<4:30"), (4.5 * 60, 5 * 60, "4:30-5:00"), (5 * 60, 5.5 * 60, "5:00-5:30"),
                (5.5 * 60, 6 * 60, "5:30-6:00"), (6 * 60, 6.5 * 60, "6:00-6:30"), (6.5 * 60, 99 * 60, ">6:30")]
        pace = 1000 / np.maximum(w, 0.3)
        rows = []
        for lo, hi, lab in bins:
            mk = (pace >= lo) & (pace < hi) & (w > 1.5) & ~np.isnan(H[:len(w)])
            if mk.sum() > 20:
                rows.append("%s: HR %.0f (%d s)" % (lab, H[:len(w)][mk].mean(), mk.sum()))
        if rows:
            print("HR at pace: " + "; ".join(rows))
    # loop length: first return to the start point
    ds = haversine(a[0, 1], a[0, 2], a[:, 1], a[:, 2])
    cand = np.where((cum > 400) & (ds < 25))[0]
    if len(cand):
        first = cand[0]
        j = first + int(np.argmin(ds[first:first + 60]))
        print("Loop check: first return to the start point after %.0f m" % cum[j])
    if target and cum[-1] >= target:
        print("Moving time at %.0f m: %s (elapsed %s)" % (target, fmt_t(at(target)), fmt_t(float(np.interp(target, cum, t - t[0])))))
    elif target:
        print("Target %.0f m not reached (recorded %.0f m)" % (target, cum[-1]))



# ----------------------------------------------------------------------------- v2 additions
import gzip
import io
import os

_EX = {}   # extras of the file being analysed (recorded distance / speed from FIT)

DUR = [(5, "5s"), (15, "15s"), (30, "30s"), (60, "1min"), (120, "2min"), (180, "3min"), (300, "5min"), (480, "8min"),
       (600, "10min"), (900, "15min"), (1200, "20min"), (1800, "30min"), (2700, "45min"), (3600, "60min"),
       (5400, "90min"), (7200, "120min"), (9000, "150min"), (10800, "180min")]


def _fill(ts, x):
    ok = np.isfinite(x)
    if ok.sum() >= 2 and (~ok).any():
        x = np.interp(ts, ts[ok], x[ok])
    return x


def load_fit(path):
    from fitparse import FitFile
    raw = gzip.open(path, "rb").read() if path.lower().endswith(".gz") else open(path, "rb").read()
    rows = {}
    for m in FitFile(io.BytesIO(raw)).get_messages("record"):
        v = m.get_values()
        ts = v.get("timestamp")
        if ts is None:
            continue
        d = rows.setdefault(ts.replace(tzinfo=timezone.utc).timestamp(), {})
        for k, val in v.items():
            if val is not None and k not in d and isinstance(val, (int, float)):
                d[k] = val
    if not rows:
        raise SystemExit("no record messages in %s" % path)
    ts = np.array(sorted(rows))

    def col(*keys):
        out = np.full(len(ts), np.nan)
        for i, t in enumerate(ts):
            for k in keys:
                if k in rows[t]:
                    out[i] = rows[t][k]
                    break
        return out
    sc = 180.0 / 2 ** 31
    la, lo = _fill(ts, col("position_lat") * sc), _fill(ts, col("position_long") * sc)
    ele = _fill(ts, col("enhanced_altitude", "altitude"))
    a = np.column_stack([ts, la, lo, ele, col("power"), col("heart_rate"), col("cadence"), col("temperature")])
    ex = {"dist": _fill(ts, col("distance")), "speed": _fill(ts, col("enhanced_speed", "speed"))}
    return a, ex


def load_any(path):
    p = path.lower()
    if p.endswith(".fit") or p.endswith(".fit.gz"):
        return load_fit(path)
    return load_gpx(path), {}


def ensure_speed(tl, a):
    if np.isfinite(tl["S"]).sum() > 30:
        return
    t = a[:, 0]
    d = haversine(a[:-1, 1], a[:-1, 2], a[1:, 1], a[1:, 2])
    sp = np.concatenate([[0], d / np.maximum(np.diff(t), 1)])
    S = np.full(len(tl["rec"]), np.nan)
    S[(t - t[0]).astype(int)] = sp
    tl["S"] = S


def moving_mask(tl, thr=1.0):
    return tl["rec"] & (np.nan_to_num(tl["S"], nan=0.0) >= thr)


def curves(tl, thr=1.0):
    """{label: (elapsed-based, stops-excluded)}.  elapsed-based = Strava power-curve convention (paused/stopped seconds
    count as 0 W); stops-excluded ('rolling') = only recorded seconds with speed >= thr, coasting (0 W) kept."""
    P, rec = tl["P"], tl["rec"]
    el = np.where(rec, np.nan_to_num(P), 0.0)
    ro = np.nan_to_num(P)[moving_mask(tl, thr)]
    return {lab: (mean_max(el, d), mean_max(ro, d)) for d, lab in DUR}


def print_curves(tl, thr=1.0):
    c = curves(tl, thr)
    print("Mean-max power, elapsed-based (Strava convention) | stops excluded, coasting kept:")
    for lab in [l for _, l in DUR]:
        e, r = c[lab]
        if np.isfinite(e) or np.isfinite(r):
            print("   %-6s %5s W | %5s W" % (lab, "-" if not np.isfinite(e) else "%.0f" % e, "-" if not np.isfinite(r) else "%.0f" % r))


def ride_metrics(tl, a, ftp, z2cap, thr=1.0):
    P, H, C, T, rec = tl["P"], tl["H"], tl["C"], tl["T"], tl["rec"]
    mv = moving_mask(tl, thr)
    m = rec & ~np.isnan(P)
    p = P[m]
    out = {"elapsed_s": len(rec), "recorded_s": int(rec.sum()), "moving_s": int(mv.sum())}
    if len(p) < 60:
        return out
    pm = np.nan_to_num(P)[mv]
    npw = norm_power(p)
    out.update(avg_w_moving=pm.mean(), avg_w_recorded=p.mean(), np_w=npw, vi=npw / p.mean(), max_w=p.max(),
               if_=npw / ftp, tss_like=len(p) / 3600 * (npw / ftp) ** 2 * 100, kj=p.sum() / 1000)
    ps = np.convolve(p, np.ones(3) / 3, mode="same")
    edges = [0, .55, .75, .90, 1.05, 1.20, 1.50, 99]
    for i in range(7):
        out["z%d_min" % (i + 1)] = ((ps / ftp >= edges[i]) & (ps / ftp < edges[i + 1])).sum() / 60
    out["pct_le_cap"] = (ps <= z2cap).mean() * 100
    hh = H[rec]
    hh = hh[~np.isnan(hh)]
    if len(hh) > 120:
        out.update(hr_avg=hh.mean(), hr_max=hh.max(), hr_max30=np.convolve(hh, np.ones(30) / 30, mode="valid").max(),
                   hr_flags=len(hr_quality(H)))
    c = C[rec]
    c = c[(c > 0) & ~np.isnan(c)]
    if len(c):
        out.update(cad_mean=c.mean(), cad_lt70=(c < 70).mean() * 100, cad_85_95=((c >= 85) & (c <= 95)).mean() * 100)
    t_ok = T[~np.isnan(T)]
    if len(t_ok):
        out["temp_c"] = t_ok.mean()
    cu = curves(tl, thr)
    for lab, (e, r) in cu.items():
        out["el_" + lab] = e
        out["ro_" + lab] = r
    return out


def best_over_distance(cum, mt, dist):
    """fastest time (moving-time axis) over `dist` metres, window start at every sample."""
    if cum[-1] < dist:
        return float("nan")
    j = np.searchsorted(cum, cum + dist)
    ok = j < len(cum)
    i = np.where(ok)[0]
    j = j[ok]
    j0 = np.maximum(j - 1, 0)
    frac = (cum[i] + dist - cum[j0]) / np.maximum(cum[j] - cum[j0], 1e-9)
    t_end = mt[j0] + frac * (mt[j] - mt[j0])
    return float((t_end - mt[i]).min())


def run_metrics(a, ex):
    t = a[:, 0]
    d = haversine(a[:-1, 1], a[:-1, 2], a[1:, 1], a[1:, 2])
    cum = np.concatenate([[0], np.cumsum(d)])
    if ex.get("dist") is not None and np.isfinite(ex["dist"]).all():
        cum = np.asarray(ex["dist"], float) - float(ex["dist"][0])
        d = np.diff(cum)
    dt = np.diff(t)
    stop = (dt > 2.5) & (d / np.maximum(dt, 1) < 1.0)
    mt = np.concatenate([[0], np.cumsum(np.where(stop, 0.0, dt))])
    H = a[:, 5]
    out = {"elapsed_s": t[-1] - t[0], "moving_s": mt[-1], "dist_km": cum[-1] / 1000,
           "pace_moving": mt[-1] / (cum[-1] / 1000)}
    hv = H[~np.isnan(H)]
    if len(hv) > 30:
        out.update(hr_avg=hv.mean(), hr_max=hv.max(), hr_flags=len(hr_quality(H)))
    splits, prev = [], 0.0
    for k in range(1, int(cum[-1] // 1000) + 1):
        s = float(np.interp(k * 1000, cum, mt))
        splits.append(fmt_t(s - prev))
        prev = s
    out["splits_km"] = " ".join(splits)
    for dd, lab in ((400, "400m"), (1000, "1k"), (1609.34, "mile"), (3218.69, "2mile"), (5000, "5k")):
        out["best_" + lab] = best_over_distance(cum, mt, dd)
    return out


def _single(args):
    global _EX
    a, ex = load_any(args.file)
    _EX = ex
    tl = timeline(a, ex)
    ensure_speed(tl, a)
    t0 = datetime.fromtimestamp(a[0, 0], timezone.utc)
    try:
        from zoneinfo import ZoneInfo
        t0 = t0.astimezone(ZoneInfo(args.tz))
    except Exception:
        pass
    print("File: %s" % args.file)
    print("Start: %s | points %d | elapsed %s" % (t0.strftime("%Y-%m-%d %H:%M %Z"), len(a), fmt_t(a[-1, 0] - a[0, 0])))
    if (~np.isnan(tl["P"])).sum() > 60:
        print("Type: ride with power")
        ride_report(tl, a, args.ftp, args.z2cap)
        print_curves(tl, args.stop_speed)
        mv = moving_mask(tl, args.stop_speed)
        print("Moving (speed >= %.1f m/s) %s of %s recorded, %s elapsed" % (args.stop_speed, fmt_t(mv.sum()), fmt_t(tl["rec"].sum()), fmt_t(len(tl["rec"]))))
    else:
        print("Type: run / no power")
        run_report(tl, a, args.lap, args.target)
        rm = run_metrics(a, ex)
        print("Best efforts (moving time): " + ", ".join("%s %s" % (k[5:], fmt_t(v)) for k, v in rm.items() if k.startswith("best_") and np.isfinite(v)))
    flags = hr_quality(tl["H"])
    print("Data-quality flags: " + ("none" if not flags else ""))
    for f in flags:
        print("   - " + f)


def _batch(args):
    import pandas as pd
    global _EX
    raw = pd.read_csv(args.csv)
    os.makedirs(args.out, exist_ok=True)
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(args.tz)
    except Exception:
        tz = timezone.utc
    rides, runs = [], []
    for _, r in raw.iterrows():
        fn = os.path.join(args.batch, os.path.basename(str(r["Filename"])))
        if not os.path.exists(fn):
            print("missing file:", fn)
            continue
        a, ex = load_any(fn)
        _EX = ex
        tl = timeline(a, ex)
        ensure_speed(tl, a)
        start = datetime.strptime(r["Activity Date"], "%b %d, %Y, %I:%M:%S %p").replace(tzinfo=timezone.utc).astimezone(tz)
        base = {"date": start.strftime("%Y-%m-%d"), "time": start.strftime("%H:%M"), "name": r["Activity Name"],
                "type": r["Activity Type"], "file": os.path.basename(fn)}
        if r["Activity Type"] == "Run":
            runs.append({**base, **run_metrics(a, ex)})
        else:
            rm = ride_metrics(tl, a, args.ftp, args.z2cap, args.stop_speed)
            rm["dist_km"] = (ex["dist"][-1] - ex["dist"][0]) / 1000 if ex.get("dist") is not None else float(
                np.nansum(haversine(a[:-1, 1], a[:-1, 2], a[1:, 1], a[1:, 2])) / 1000)
            rides.append({**base, **rm})
    pd.DataFrame(rides).round(2).to_csv(os.path.join(args.out, "digest_rides.csv"), index=False)
    pd.DataFrame(runs).round(2).to_csv(os.path.join(args.out, "digest_runs.csv"), index=False)
    print("rides %d, runs %d -> %s" % (len(rides), len(runs), args.out))


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?")
    ap.add_argument("--ftp", type=float, default=175)
    ap.add_argument("--z2cap", type=float, default=135)
    ap.add_argument("--lap", type=float, default=1250)
    ap.add_argument("--target", type=float, default=0)
    ap.add_argument("--tz", default="Europe/Berlin")
    ap.add_argument("--stop-speed", type=float, default=1.0)
    ap.add_argument("--batch")
    ap.add_argument("--csv")
    ap.add_argument("--out", default="digest")
    args = ap.parse_args()
    if args.batch:
        if not args.csv:
            raise SystemExit("--batch needs --csv")
        _batch(args)
    elif args.file:
        _single(args)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()

"""segments_tool.py - Strava segments: reference geometry, effort archive and PR fingerprinting (v1.4, 2026-11-12).

Strava's connector has no segment tool and the bulk export has no segment efforts, so this rebuilds them from the ride files:
  1. segments.json holds each segment's metadata (Pat's Strava values) and a 25-point reference line along its course. The line was taken from
     the ride in which the PR was set, found by its fingerprint (elapsed time, distance, avg power, cadence, HR avg/max).
  2. find_efforts() scans every ride for passes: a start crossing (within 40 m), the next end crossing 0.8-1.3 x the length later, the course
     within 40 m of every reference point, in the right order (out-and-back passes are rejected). Validated against Strava's own efforts on
     27 Sep: time within 0-3 s, power within about 1 W, HR within 0.2 bpm.
  3. build_archive() -> one row per effort; only real efforts are tracked (elapsed-based power >= 80% of the PR power, see is_tracked);
     HR is checked for strap artefacts (hr_flag) and blanked for rides Pat marked unusable (segments.json 'hr_unusable');
     archive_md() -> markdown tables for the segments.md Project doc. Thresholds live in segments.json ('tracking', 'hr_check').

Conventions: power and cadence are averaged over the recorded samples; this equals Strava's segment values when the effort has no
auto-paused stop. Garmin auto-pause drops records while stopped (`stopped_s` shows standing time inside the effort); Strava then counts
the stop as 0 W, i.e. its segment power equals the elapsed-based `w_el` (31 Oct Long and windy road, 67 s stop: Strava 147 W, w 157 W,
w_el 148 W), and the stop flag shows w_el. Time is elapsed. Power is on the Stages scale (left-only meter).
Usage:
    python3 segments_tool.py                       # newest strava_export_*.zip + tests/*.fit -> segments_archive.csv, prints markdown
    import segments_tool as st; acts = st.load_rides(); st.fingerprint(acts, km=1.56, time_s=221, w=248, cad=88, hr=183, hrmax=189)
New segment: take its PR values from Strava, run fingerprint(), check the best candidate (score near 0-3, distance and climb plausible),
then add_segment() and save_segments(). Segments without power/HR on the PR ride need `dalt` and a check of the effort count.
"""
import os, io, re, gzip, glob, json, zipfile
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
TZ = "Europe/Berlin"
SC = 180 / 2 ** 31
RIDER_KG = 56.0          # Pat 12 Nov, measured (60 kg until v1.3 was never weighed); only the W/kg column depends on it


def hav(a, b, c, d):
    """Haversine distance in metres (arrays allowed)."""
    R = 6371000.0; a, b, c, d = map(np.radians, (a, b, c, d))
    return 2 * R * np.arcsin(np.sqrt(np.sin((c - a) / 2) ** 2 + np.cos(a) * np.cos(c) * np.sin((d - b) / 2) ** 2))


# ----------------------------------------------------------------------------- LOADING
def _from_fit_bytes(raw):
    from fitparse import FitFile
    rows = []
    for m in FitFile(io.BytesIO(raw)).get_messages("record"):
        v = m.get_values()
        rows.append((v.get("timestamp"), v.get("position_lat"), v.get("position_long"), v.get("distance"),
                     v.get("enhanced_altitude", v.get("altitude")), v.get("power"), v.get("heart_rate"), v.get("cadence")))
    sess = list(FitFile(io.BytesIO(raw)).get_messages("session"))
    sport = [m.get_value("sport") for m in sess]; sub = [m.get_value("sub_sport") for m in sess]
    df = pd.DataFrame(rows, columns=["ts", "lat", "lon", "dist", "alt", "p", "hr", "cad"])
    df = df[df.ts.notna()]
    t = (pd.to_datetime(df.ts, utc=True) - pd.Timestamp("1970-01-01", tz="UTC")).dt.total_seconds().values
    f = lambda c: pd.to_numeric(df[c], errors="coerce").astype(float).values
    return dict(t=t, lat=f("lat") * SC, lon=f("lon") * SC, dist=f("dist"), alt=f("alt"), p=f("p"), hr=f("hr"), cad=f("cad"), sport=str(sport[0] if sport else ""), sub_sport=str(sub[0] if sub else ""))


def _from_gpx_text(txt):
    pts = re.findall(r'<trkpt lat="([^"]+)" lon="([^"]+)">(.*?)</trkpt>', txt, re.S)
    def g(pat, body):
        m = re.search(pat, body); return float(m.group(1)) if m else np.nan
    la = np.array([float(a) for a, _, _ in pts]); lo = np.array([float(b) for _, b, _ in pts])
    t = np.array([pd.Timestamp(re.search(r"<time>([^<]+)</time>", body).group(1)).timestamp() for _, _, body in pts])
    d = np.r_[0, np.cumsum(hav(la[:-1], lo[:-1], la[1:], lo[1:]))] if len(la) > 1 else np.zeros(len(la))
    return dict(t=t, lat=la, lon=lo, dist=d, alt=np.array([g(r"<ele>([^<]+)</ele>", b) for _, _, b in pts]),
                p=np.array([g(r"<power>([^<]+)<", b) for _, _, b in pts]), hr=np.array([g(r"hr>([^<]+)<", b) for _, _, b in pts]),
                cad=np.array([g(r"cad>([^<]+)<", b) for _, _, b in pts]))


def _newest_export():
    def key(p):
        m = re.search(r"_(\d\d)_(\d\d)\.zip$", p); return (int(m.group(2)), int(m.group(1))) if m else (0, 0)
    z = sorted(glob.glob(os.path.join(HERE, "strava_export_*.zip")) + glob.glob(os.path.join(HERE, "data", "strava_export_*.zip")), key=key)
    return z[-1] if z else None


def load_rides(export_zip=None, extra=None, cache_dir=None, show=True):
    """Outdoor rides from the Strava export zip (Ride / E-Bike Ride; virtual rides skipped) plus extra FIT files (default tests/*.fit
    that are rides). Returns {key: dict(t, lat, lon, dist, alt, p, hr, cad, name)}; key = Strava activity id or the file name.
    Duplicates (same start within 2 min) are dropped, keeping the export copy. cache_dir: optional folder for .npz caches."""
    export_zip = export_zip or _newest_export(); acts = {}
    if export_zip:
        with zipfile.ZipFile(export_zip) as z:
            csv = pd.read_csv(z.open([n for n in z.namelist() if n.endswith("activities.csv")][0]))
            for _, r in csv.iterrows():
                if str(r["Activity Type"]) not in ("Ride", "E-Bike Ride") or not isinstance(r["Filename"], str): continue
                key = str(r["Activity ID"]); cp = os.path.join(cache_dir, key + ".npz") if cache_dir else None
                if cp and os.path.exists(cp): acts[key] = dict(np.load(cp)); continue
                raw = z.read(r["Filename"]); fn = r["Filename"]
                if fn.endswith(".gz"): raw = gzip.decompress(raw); fn = fn[:-3]
                if fn.endswith(".fit"): a = _from_fit_bytes(raw)
                elif fn.endswith(".gpx"): a = _from_gpx_text(raw.decode("utf-8", "ignore"))
                else: continue
                if not np.isfinite(a["lat"]).any(): continue
                acts[key] = a
                if cp: os.makedirs(cache_dir, exist_ok=True); np.savez(cp, **a)
    for f in (extra if extra is not None else sorted(glob.glob(os.path.join(HERE, "tests", "*.fit")))):
        try: a = _from_fit_bytes(open(f, "rb").read())
        except Exception: continue
        if a.get("sport") not in ("cycling", "e_biking") or a.get("sub_sport") in ("virtual_activity", "indoor_cycling") \
                or not np.isfinite(a["lat"]).any() or np.nanmax(a["dist"]) < 2000: continue   # runs, trainer and virtual (MyWhoosh) files
        if any(abs(b["t"][0] - a["t"][0]) < 120 for b in acts.values()): continue
        acts[os.path.basename(f)] = a
    if show: print("rides loaded: %d (%s)" % (len(acts), os.path.basename(export_zip) if export_zip else "no export"))
    return acts


# ----------------------------------------------------------------------------- SEGMENTS
def load_segments(path=None):
    """segments.json -> dict (meta + list 'segments')."""
    return json.load(open(path or os.path.join(HERE, "segments.json"), encoding="utf-8"))


def save_segments(data, path=None):
    json.dump(data, open(path or os.path.join(HERE, "segments.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def fingerprint(acts, km, time_s, w=None, cad=None, hr=None, hrmax=None, dalt=None, n=5, tol_km=None, show=True):
    """Find the ride window that matches a Strava effort: exact elapsed time, distance within 6%, then score by |W|+|cad|+|HR|+|HRmax|
    (+|dalt| if given, for rides without power). Returns candidates [(score, key, i0, i1, km, w, cad, hr, hrmax, dalt)] best first."""
    tol_km = tol_km or 0.06 * km + 0.03; out = []
    for key, a in acts.items():
        t, d = a["t"], a["dist"]
        if len(t) < 3: continue
        j = np.searchsorted(t, t + time_s); ok = j < len(t); i = np.where(ok)[0]; j = j[ok]
        ex = t[j] - t[i] == time_s; i, j = i[ex], j[ex]
        m = np.abs((d[j] - d[i]) / 1000 - km) < tol_km
        for i0, i1 in zip(i[m], j[m]):
            s = slice(i0, i1 + 1); P, H, C, A = a["p"][s], a["hr"][s], a["cad"][s], a["alt"][s]
            ww = np.nanmean(np.nan_to_num(P)) if np.isfinite(P).any() else np.nan
            hh = np.nanmean(H) if np.isfinite(H).any() else np.nan
            hm = np.nanmax(H) if np.isfinite(H).any() else np.nan
            cc = np.nanmean(C[C > 0]) if (C > 0).any() else np.nan
            da = A[-1] - A[0] if np.isfinite(A[[0, -1]]).all() else np.nan
            sc = abs((d[i1] - d[i0]) / 1000 - km) * 50
            for want, got, pen in ((w, ww, 50), (cad, cc, 20), (hr, hh, 30), (hrmax, hm, 30), (dalt, da, 30)):
                if want is not None: sc += abs(got - want) if np.isfinite(got) else pen
            out.append((round(sc, 1), key, int(i0), int(i1), (d[i1] - d[i0]) / 1000, ww, cc, hh, hm, da))
    out.sort(key=lambda x: x[0]); best = []
    for c in out:
        if any(c[1] == b[1] and abs(c[2] - b[2]) < 60 for b in best): continue
        best.append(c)
        if len(best) == n: break
    if show:
        for c in best:
            print("score %6.1f  %-14s %s  idx %d-%d  %.3f km  W %.1f cad %.1f HR %.1f/%.0f  dAlt %+.1f" % (
                c[0], c[1], _local(acts[c[1]]["t"][c[2]]).strftime("%d.%m.%Y %H:%M"), c[2], c[3], c[4], c[5], c[6], c[7], c[8], c[9]))
    return best


def ref_from(a, i0, i1, n=25):
    """25-point reference line (lat, lon) from samples i0..i1 of ride a, evenly spaced by distance."""
    d = a["dist"][i0:i1 + 1]; tgt = np.linspace(d[0], d[-1], n); k = np.searchsorted(d, tgt).clip(0, len(d) - 1)
    return dict(lat=[round(float(x), 6) for x in a["lat"][i0:i1 + 1][k]], lon=[round(float(x), 6) for x in a["lon"][i0:i1 + 1][k]],
                km=round(float((d[-1] - d[0]) / 1000), 3), src_start_utc=float(a["t"][i0]))


def add_segment(data, a, i0, i1, sid, name, place, km, time_s, method="fingerprint of the PR effort", **meta):
    """Add or replace a segment in `data` with geometry from ride a, samples i0..i1 (from fingerprint())."""
    seg = dict(id=int(sid), name=name, place=place, status="attempted", km=km, strava_pr=dict(time_s=time_s), ref=dict(ref_from(a, i0, i1), method=method))
    seg.update(meta); data["segments"] = [s for s in data["segments"] if s["id"] != int(sid)] + [seg]; return seg


def find_efforts(acts, ref, rad=40.0, trk=40.0):
    """All passes of one segment over all rides (see module docstring). Returns a list of dicts sorted by time."""
    out = []; RL, RO = np.array(ref["lat"]), np.array(ref["lon"]); L = ref["km"] * 1000
    for key, a in acts.items():
        la, lo, t, d = a["lat"], a["lon"], a["t"], a["dist"]; ok = np.isfinite(la)
        if not ok.any(): continue
        ds = np.where(ok, hav(la, lo, RL[0], RO[0]), 1e9); de = np.where(ok, hav(la, lo, RL[-1], RO[-1]), 1e9)
        def passes(dd):
            near = np.where(dd < rad)[0]
            return [g[np.argmin(dd[g])] for g in np.split(near, np.where(np.diff(near) > 5)[0] + 1)] if len(near) else []
        S, used = passes(ds), set()
        for j in passes(de):
            cand = [i for i in S if i < j and 0.8 * L < d[j] - d[i] < 1.3 * L]
            if not cand: continue
            i = max(cand)                                       # latest start crossing before this end, as Strava does
            if i in used: continue
            sla, slo = la[i:j + 1], lo[i:j + 1]
            nn = [int(np.argmin(hav(sla, slo, x, y))) for x, y in zip(RL, RO)]
            dev = max(float(hav(sla[k], slo[k], x, y)) for k, x, y in zip(nn, RL, RO))
            if dev > trk or np.any(np.diff(nn) < -3): continue    # off course, or wrong direction
            used.add(i); s = slice(i, j + 1); P, H, C, A = a["p"][s], a["hr"][s], a["cad"][s], a["alt"][s]
            dt, dd = np.diff(t[s]), np.diff(d[s]); el = float(t[j] - t[i])
            sm = pd.Series(A).rolling(15, center=True, min_periods=1).mean().values
            out.append(dict(key=key, start=_local(t[i]), time_s=el, km=float((d[j] - d[i]) / 1000),
                            w=float(np.nanmean(np.nan_to_num(P))) if np.isfinite(P).any() else np.nan,
                            cad=float(np.nanmean(C[C > 0])) if (C > 0).any() else np.nan,
                            hr=float(np.nanmean(H)) if np.isfinite(H).any() else np.nan,
                            hrmax=float(np.nanmax(H)) if np.isfinite(H).any() else np.nan,
                            dalt=float(A[-1] - A[0]) if np.isfinite(A[[0, -1]]).all() else np.nan,
                            gain=float(np.nansum(np.clip(np.diff(sm), 0, None))),
                            stopped_s=float(el - np.sum(dt[(dd > 0.5) & (dt <= 3)])), i=int(i), j=int(j), maxdev_m=dev,
                            w_el=float(np.nansum(np.nan_to_num(P[1:]) * np.minimum(dt, 2.0)) / el) if np.isfinite(P).any() and el > 0 else np.nan,
                            hr_start=float(np.nanmean(H[:10])) if np.isfinite(H[:10]).any() else np.nan,
                            hr_end=float(np.nanmean(H[-10:])) if np.isfinite(H[-10:]).any() else np.nan,
                            hr_cov=float((np.isfinite(H) & (H > 0)).mean()) if len(H) else 0.0,
                            ride_min=float((t[i] - t[0]) / 60), ride_min_end=float((t[j] - t[0]) / 60)))
    return sorted(out, key=lambda x: x["start"])


def _local(ts):
    return pd.Timestamp(ts, unit="s", tz="UTC").tz_convert(TZ)


# ----------------------------------------------------------------------------- ARCHIVE
DEFAULTS = dict(tracking=dict(min_rel_power=0.80, time_factor_climb=1.25, time_factor_flat=1.08, climb_grade_pct=3.0),
                hr_check=dict(min_w=200.0, min_s=30.0, end_hr=145.0, long_s=120.0, avg_hr_long=140.0, drop_bpm=5.0,
                              mod_w=150.0, mod_s=120.0, mod_end_hr=135.0, min_cov=0.8))


def _cfg(data, k):
    return {**DEFAULTS[k], **(data.get(k) or {})}


def hr_unusable(data, e):
    """Note text if Pat marked the HR of this ride (or a minute range of it) as unusable in segments.json 'hr_unusable', else ''."""
    u = (data.get("hr_unusable") or {}).get(str(e["key"]))
    if not u: return ""
    if isinstance(u, str): return u
    lo, hi = u.get("from_min", 0), u.get("to_min", 1e9)
    return u.get("note", "HR unusable") if e["ride_min_end"] >= lo and e["ride_min"] <= hi else ""


def hr_flag(e, cfg=None):
    """'HR?' when the HR cannot be right for the power (strap artefact). Average HR alone is not enough: HR lags 30-90 s, so genuine
    45-s efforts at 200+ W often average only 128-142 bpm (rising from about 100-125 to 155-170). Flag an effort of >= min_s at >= min_w
    when HR at its end (last 10 s) is below end_hr, when HR falls by more than drop_bpm across it, or when an effort of >= long_s
    averages below avg_hr_long; also an effort of >= mod_s at >= mod_w ending below mod_end_hr (5 Sep: 75-130 bpm at 180 W), and
    'HR partial' when less than min_cov of the effort has HR. Defaults for Pat in Nov 2026: 200 W, 30 s, end 145, 2 min / 140, drop 5;
    150 W / 2 min / 135; coverage 80% (raise them as fitness changes)."""
    c = {**DEFAULTS["hr_check"], **(cfg or {})}
    if np.isfinite(e.get("hr", np.nan)) and e.get("hr_cov", 1.0) < c["min_cov"]: return "HR partial"
    if not (np.isfinite(e.get("hr", np.nan)) and np.isfinite(e.get("w", np.nan))): return ""
    if e["w"] >= c["mod_w"] and e["time_s"] >= c["mod_s"] and np.isfinite(e.get("hr_end", np.nan)) and e["hr_end"] < c["mod_end_hr"]: return "HR?"
    if e["w"] < c["min_w"] or e["time_s"] < c["min_s"]: return ""
    if np.isfinite(e.get("hr_end", np.nan)) and e["hr_end"] < c["end_hr"]: return "HR?"
    if np.isfinite(e.get("hr_start", np.nan)) and np.isfinite(e.get("hr_end", np.nan)) and e["hr_start"] - e["hr_end"] > c["drop_bpm"]: return "HR?"
    if e["time_s"] >= c["long_s"] and e["hr"] < c["avg_hr_long"]: return "HR?"
    return ""


def is_tracked(e, pr, grade_pct, cfg=None):
    """Keep an effort in the archive if it was a real effort: elapsed-based power (standing time counts as 0 W, so efforts with stops
    drop out unless they are still strong) >= min_rel_power x the power of the current PR effort. Without power on either side, use
    time: <= time_factor x PR time (1.25 on climbs >= climb_grade_pct, 1.08 elsewhere; power ~ speed^3 on the flat, ~ speed on climbs)."""
    c = cfg or DEFAULTS["tracking"]
    if e is pr: return True
    if np.isfinite(e.get("w_el", np.nan)) and np.isfinite(pr.get("w", np.nan)):
        return e["w_el"] >= c["min_rel_power"] * pr["w"]
    f = c["time_factor_climb"] if (grade_pct or 0) >= c["climb_grade_pct"] else c["time_factor_flat"]
    return e["time_s"] <= f * pr["time_s"]


def build_archive(acts=None, data=None, show=True):
    """One row per effort for every attempted segment, with `tracked` (see is_tracked) and HR checks. Columns: id, name, date, start,
    time_s, km, kmh, w (moving, as Strava), w_el (elapsed-based), wkg, cad, hr, hrmax, hr_end, dalt, gain, stopped_s, rank (by time),
    pr_gap_s, rel_w (w_el / PR power), tracked, flags. HR of rides Pat marked unusable is blanked. Prints found / tracked / Strava counts."""
    acts = acts if acts is not None else load_rides(); data = data or load_segments(); rows = []
    tc, hc = _cfg(data, "tracking"), _cfg(data, "hr_check")
    for s in data["segments"]:
        if not s.get("ref"): continue
        ef = find_efforts(acts, s["ref"])
        if not ef: continue
        pr = min(ef, key=lambda x: x["time_s"])
        for e in ef:
            fl = []; un = hr_unusable(data, e)
            if un: fl.append(un); e["hr"] = e["hrmax"] = e["hr_end"] = np.nan
            else:
                f = hr_flag(e, hc)
                if f: fl.append(f)
            if e["stopped_s"] >= 5:
                gap = np.isfinite(e["w"]) and np.isfinite(e["w_el"]) and abs(e["w"] - e["w_el"]) >= 3
                fl.append("stop %ds" % e["stopped_s"] + (" (elapsed-based %.0f W, as Strava)" % e["w_el"] if gap else ""))
            rows.append(dict(id=s["id"], name=s["name"], date=e["start"].strftime("%Y-%m-%d"), start=e["start"].strftime("%H:%M"),
                             time_s=e["time_s"], km=e["km"], kmh=e["km"] / e["time_s"] * 3600, w=e["w"], w_el=e["w_el"], wkg=e["w"] / RIDER_KG,
                             cad=e["cad"], hr=e["hr"], hrmax=e["hrmax"], hr_end=e["hr_end"], dalt=e["dalt"], gain=e["gain"], stopped_s=e["stopped_s"],
                             rel_w=e["w_el"] / pr["w"] if np.isfinite(pr["w"]) else np.nan, tracked=is_tracked(e, pr, s.get("grade_pct"), tc),
                             flags=", ".join(fl), strava_efforts=(s.get("strava_pr") or {}).get("efforts"), key=e["key"]))
    df = pd.DataFrame(rows)
    if len(df):
        df["rank"] = df.groupby("id")["time_s"].rank(method="min").astype(int)
        df["pr_gap_s"] = df["time_s"] - df.groupby("id")["time_s"].transform("min")
    if show and len(df):
        c = df.groupby(["id", "name"]).agg(found=("time_s", "size"), tracked=("tracked", "sum")).reset_index()
        c["strava"] = c["id"].map({s["id"]: (s.get("strava_pr") or {}).get("efforts") for s in data["segments"]})
        print(c.to_string(index=False))
    return df


def _f(x, fmt="%.0f"):
    return fmt % x if isinstance(x, (int, float, np.floating)) and np.isfinite(x) else "-"


def _mmss(s):
    s = int(round(s)); return "%d:%02d" % (s // 60, s % 60)


def archive_md(df, data=None, asof=""):
    """Markdown for segments.md: overview table (all efforts found / tracked / Strava count) + one table per segment with the tracked
    efforts only (newest first)."""
    data = data or load_segments(); segs = {s["id"]: s for s in data["segments"]}; L = []
    tr = df[df["tracked"]] if "tracked" in df else df
    L.append("| ID | Segment | Place | km | Gain m | Grade % | Strava PR | Efforts found / Strava | Tracked | Best W (tracked) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for sid, s in segs.items():
        if s["status"] != "attempted": continue
        g = df[df.id == sid]; t = tr[tr.id == sid]; pr = s.get("strava_pr") or {}
        L.append("| [%d](https://www.strava.com/segments/%d) | %s | %s | %.2f | %s | %s | %s | %d / %s | %d | %s |" % (
            sid, sid, s["name"], s["place"], s["km"], s.get("gain_m", "-"), s.get("grade_pct", "-"), _mmss(pr.get("time_s", 0)),
            len(g), pr.get("efforts", "-"), len(t), _f(t["w"].max()) if len(t) and t["w"].notna().any() else "-"))
    for sid, s in segs.items():
        g = tr[tr.id == sid].sort_values(["date", "start"], ascending=False)
        if not len(g): continue
        hidden = int((df.id == sid).sum() - len(g))
        L.append(""); L.append("### %s (%d), %.2f km, %s m, %s %%%s" % (s["name"], sid, s["km"], s.get("gain_m", "-"), s.get("grade_pct", "-"), " - " + s["note"] if s.get("note") else ""))
        L.append("| Date | Time | Rank | km/h | W | W/kg | % of PR W | Cad | HR avg/max | Notes |"); L.append("|---|---|---|---|---|---|---|---|---|---|")
        for _, r in g.iterrows():
            L.append("| %s %s | %s | %d | %.1f | %s | %s | %s | %s | %s/%s | %s |" % (r["date"], r["start"], _mmss(r["time_s"]), r["rank"], r["kmh"], _f(r["w"]),
                     _f(r["wkg"], "%.2f"), _f(r["rel_w"] * 100) if np.isfinite(r["rel_w"]) else "-", _f(r["cad"]), _f(r["hr"]), _f(r["hrmax"]),
                     r["flags"] if isinstance(r["flags"], str) else ""))
        if hidden: L.append("%d more effort(s) below the tracking threshold not listed." % hidden)
    return "\n".join(L)


if __name__ == "__main__":
    acts = load_rides()
    df = build_archive(acts)
    out = os.path.join(HERE, "segments_archive.csv"); t = df[df["tracked"]]
    t.drop(columns=["key", "tracked"]).round(1).assign(wkg=t["wkg"].round(2), rel_w=t["rel_w"].round(3)).to_csv(out, index=False)
    print("written", out, len(t), "tracked efforts of", len(df))
    print(archive_md(df))
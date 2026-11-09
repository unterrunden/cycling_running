#!/usr/bin/env python3
"""selfcheck.py - regression test of the coaching toolkit (analysis_tools.py, routes_tool.py, cp_lib.py).

Run in a fresh chat after cloning the repo:   pip install fitparse scipy pandas --break-system-packages ; python3 selfcheck.py
It reproduces numbers that were validated against Strava / the chats (20 Sep ride, 22 Sep hour, route geometry, C19 loop, 5K trial, 4DP ...),
so a silent bug introduced by a script change shows up as FAIL. SKIP = the needed data file is not in the repo.
Data (repo folder, data/ or tests/): the newest strava_export_<dd_mm>.zip, every all_routes_*.zip / rides_runs_gpx_files_*.zip (zips can be
replaced by newer ones with the same name pattern); optional: tests/28_10.fit (28 Oct 5K) and tests/01_11.fit (1 Nov 4DP).
"""
import os, sys, glob, zipfile, tempfile, traceback
from datetime import date
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
RES = []


BASES = (HERE, os.path.join(HERE, "data"), os.path.join(HERE, "tests"))


def find(*names):
    for base in BASES:
        for n in names:
            p = os.path.join(base, n)
            if os.path.exists(p): return p
    return None


def find_all(pattern):
    """All files matching a glob pattern in the repo folder, data/ and tests/, newest first (by the dd_mm date in the name, else file time)."""
    import re
    out = [p for b in BASES for p in glob.glob(os.path.join(b, pattern))]
    def key(p):
        m = re.search(r"_(\d\d)_(\d\d)\.zip$", p)
        return (int(m.group(2)), int(m.group(1))) if m else (0, 0)
    return sorted(out, key=lambda p: (key(p), os.path.getmtime(p)), reverse=True)


def check(name, ok, detail=""):
    RES.append(("PASS" if ok else "FAIL", name, detail)); print("%-5s %-58s %s" % (RES[-1][0], name, detail))


def skip(name, why):
    RES.append(("SKIP", name, why)); print("%-5s %-58s %s" % ("SKIP", name, why))


def guarded(fn):
    try: fn()
    except Exception as e:
        check(fn.__name__, False, "exception: %r" % e); traceback.print_exc()


def main():
    import cp_lib as cp, routes_tool as rt, analysis_tools as at
    tmp = tempfile.mkdtemp(prefix="selfcheck_")

    # ---- pure functions
    def physics():
        d = cp.effort_distance(185, 20, 0.004); t = cp.effort_distance(185, 20, 0.004, -10); h = cp.effort_distance(185, 20, 0.004, 10)
        check("physics: 20 min at 185 W, calm / 10 km/h tail / head", 9.6 <= d <= 10.1 and 11.6 <= t <= 12.2 and 7.7 <= h <= 8.3, "%.2f / %.2f / %.2f km" % (d, t, h))
        a = cp.cp_fit([(300, 213), (600, 202)]); b = cp.cp_fit([(180, 258), (600, 202)])
        check("critical-power sketches (5/10 min and 3/10 min)", abs(cp.cp_predict(*a, 1200) - 196.5) < 1 and abs(cp.cp_predict(*b, 1200) - 190) < 1, "%.1f / %.1f W" % (cp.cp_predict(*a, 1200), cp.cp_predict(*b, 1200)))
        w = [cp.implied_headwind(173.6, 27.2, 0.0056, cda=c) for c in (0.32, 0.36, 0.40)]
        check("implied headwind of the 31 Oct block (CdA 0.32-0.40)", all(0 <= x <= 5 for x in w), str([round(x, 1) for x in w]))
    guarded(physics)

    def sun():
        ok = cp.sun_times(date(2026, 11, 29)) == ("08:10", "16:32") and cp.sun_times(date(2026, 10, 26)) == ("07:12", "17:20")
        check("sun times Cologne (29 Nov, 26 Oct incl. DST switch)", ok, str(cp.sun_times(date(2026, 11, 29))))
    guarded(sun)

    def patch():
        import io, contextlib
        p = cp.Patch(text="a\nline one\nb\n"); p.rep("b", "B"); p.insert_after("line one", "X"); p.rep("zzz", "q", "bad")
        with contextlib.redirect_stdout(io.StringIO()): fails = p.save(os.path.join(tmp, "x.txt"))
        check("Patch: records a missing target and refuses to save", len(p.fails) == 1 and bool(fails) and not os.path.exists(os.path.join(tmp, "x.txt")))
    guarded(patch)

    # ---- data-based tests
    exports = find_all("strava_export_*.zip"); exp = exports[0] if exports else None
    act_dir = csv = None
    if exp:
        zipfile.ZipFile(exp).extractall(os.path.join(tmp, "exp")); act_dir = os.path.join(tmp, "exp"); csv = os.path.join(act_dir, "activities.csv")
        print("using %s" % os.path.basename(exp))

    def csv_loader():
        df = cp.load_activities_csv(csv); old = df[df["date"] <= "2026-10-26"]; t = cp.csv_totals(old)
        check("activities.csv to 26 Oct: 43 rides / 1259.4 km, 6 runs / 33.0 km", len(old) == 49 and t["Ride"]["n"] == 43 and abs(t["Ride"]["km"] - 1259.4) < 0.2 and t["Run"]["n"] == 6 and abs(t["Run"]["km"] - 33.0) < 0.2, "%d activities in the export, %d to 26 Oct" % (len(df), len(old)))
    if csv: guarded(csv_loader)
    else: skip("activities.csv loader", "no strava_export_*.zip found")

    def ride(datestr):
        df = cp.load_activities_csv(csv); row = df[df["date"] == datestr].iloc[0]
        return os.path.join(act_dir, row["file"])

    def rides():
        f20 = ride("2026-09-20"); a, ex, tl = cp.load_activity(f20); m = at.ride_metrics(tl, a, 175, 135)
        check("20 Sep ride: avg 149 W (moving), NP 156 W", abs(m["avg_w_moving"] - 149) < 1.5 and abs(m["np_w"] - 156) < 1.5, "avg %.1f NP %.1f" % (m["avg_w_moving"], m["np_w"]))
        r = cp.ride_session(f20, show=False); dc = r["decoupling"]["decoupling_pct"]
        check("20 Sep ride: decoupling about -2%", -3.5 < dc < -1.0, "%.1f%%" % dc)
        a2, ex2, tl2 = cp.load_activity(ride("2026-09-22")); w = cp.best_window(tl2, 3600, "moving")
        check("22 Sep: best moving 60 min = 170 W (Strava avg of that ride)", abs(w["avg_w"] - 170.0) < 0.5, "%.1f W" % w["avg_w"])
        a3, ex3, tl3 = cp.load_activity(ride("2026-09-19")); w3 = cp.best_window(tl3, 3600, "elapsed")
        check("19 Sep: best elapsed 60 min = 157 W (Strava curve)", abs(w3["avg_w"] - 157.0) < 0.6, "%.1f W" % w3["avg_w"])
        i = cp.fit_inspect(f20, show=False)
        check("fit_inspect: Garmin file with laps, events, HRV", i["n_hrv"] > 1000 and i["n_laps"] >= 1 and i["records"] > 5000, "%d records, %d laps, %d hrv" % (i["records"], i["n_laps"], i["n_hrv"]))
        df, s = cp.hrv_quality(f20)
        check("hrv_quality: returns windows and a sane artefact rate", len(df) > 50 and 0 <= s["artefact_pct"] < 15, str(s))
        w20 = cp.hr_power_windows(cp.load_activity(f20)[2]); sc = cp.hr_zone_score(w20, [133, 148, 162, 173], 180)
        check("hr_power_windows / hr_zone_score on 20 Sep: windows found, scores in range", len(w20) > 50 and 0 <= sc["balanced"] <= 1, "%d windows, balanced %.2f" % (len(w20), sc["balanced"]))
        s10 = cp.hr_artefact_scan(cp.load_activity(ride("2026-09-10"))[2])
        check("hr_artefact_scan: 10 Sep strap dropouts found (min 42-58)", any(a < 50 and b > 44 for a, b, n in s10) and any(a < 58 and b > 52 for a, b, n in s10), str([(float(a), float(b), n) for a, b, n in s10]))
        s5 = cp.hr_artefact_scan(cp.load_activity(ride("2026-09-05"))[2]); g10 = cp.hr_gaps(cp.load_activity(ride("2026-09-10"))[2], 30)
        check("hr_artefact_scan 5 Sep (75-130 bpm at 180 W, min 20-29) and hr_gaps 10 Sep (km 7-14 frozen in Strava = missing)", any(a < 24 and b > 26 for a, b, n in s5) and any(a < 34 and b > 31 for a, b in g10), "%s / %s" % ([(float(a), float(b), n) for a, b, n in s5][:2], g10[:3]))
        check("fit_laps / fit_pauses: tables", len(cp.fit_laps(f20)) >= 1 and len(cp.fit_pauses(f20)) >= 0)
    if csv: guarded(rides)
    else: skip("ride tests (20/22/19 Sep)", "no strava_export_*.zip found")

    route_zips = find_all("all_routes_*.zip") + find_all("rides_runs_gpx_files_*.zip")
    for k, z in enumerate(route_zips):
        zipfile.ZipFile(z).extractall(os.path.join(tmp, "gpx", str(k)))

    def g(pat):
        hits = glob.glob(os.path.join(tmp, "gpx", "**", pat), recursive=True)
        return hits[0] if hits else None

    def routes():
        if not route_zips: return skip("route tests", "no all_routes_*.zip / rides_runs_gpx_files_*.zip found")
        c2 = g("*15km uninterrupted - komoot*")
        if c2:
            r = rt.analyse(c2); st = rt.stretches(r, by_length=True)
            check("C2 (komoot track export): 1 sharp turn, 11.7 km straight at about 172 deg", len(r["turns"]) == 1 and abs(st[0]["L"] - 11.7) < 0.2 and abs(st[0]["hd"] - 172) < 4, "%d turn(s), %.1f km at %.0f deg" % (len(r["turns"]), st[0]["L"], st[0]["hd"]))
        else: skip("C2 geometry", "15km uninterrupted GPX not found")
        c21 = g("20km uninterrupted*")
        if c21:
            r = rt.analyse(c21); st = rt.stretches(r, by_length=True)
            check("C21 (komoot route export, <rtept>): 20.0 km, 2 turns, 17.7 km straight SE", abs(r["km"] - 20.0) < 0.2 and len(r["turns"]) == 2 and abs(st[0]["L"] - 17.7) < 0.2 and abs(st[0]["hd"] - 133) < 4, "%.1f km, %d turns, %.1f km at %.0f deg" % (r["km"], len(r["turns"]), st[0]["L"], st[0]["hd"]))
        else: skip("C21 geometry (route export)", "20km uninterrupted GPX not found")
        c19 = g("*uninterrupted loop*")
        if c19:
            lc = rt.loop_closure(c19); r19 = rt.analyse(c19)
            if lc.get("join_km", 0) > 1:     # old file (until 9 Nov): 5.3 km approach + loop
                check("C19 (old file): loop joins at km 5.3, 16.4 km, +23/-21 m", lc.get("closed") and abs(lc["join_km"] - 5.3) < 0.2 and abs(lc["loop_km"] - 16.4) < 0.2 and abs(lc["loop_asc"] - 23) < 3, "join km %.1f, loop %.1f km, +%.0f m" % (lc.get("join_km", 0), lc.get("loop_km", 0), lc.get("loop_asc", 0)))
            else:                            # 9 Nov file: loop only, route export
                check("C19: loop only, 16.5 km, closes, +23 m, 4 corners", lc.get("closed") and abs(lc["loop_km"] - 16.5) < 0.2 and abs(lc["loop_asc"] - 23) < 3 and len(r19["turns"]) == 4, "loop %.1f km, +%.0f m, %d turns" % (lc.get("loop_km", 0), lc.get("loop_asc", 0), len(r19["turns"])))
        else: skip("C19 loop closure", "uninterrupted loop GPX not found")
        v1 = g("*3316196558*")
        if v1:
            r0 = rt.analyse(v1); r1 = rt.analyse(v1, merge_km=0.35)
            check("old 4dp v1: 19 raw / 17 merged turns, +152/-162 m", len(r0["turns"]) == 19 and len(r1["turns"]) == 17 and abs(r0["asc"] - 152) < 6 and abs(r0["dsc"] - 162) < 6, "%d / %d turns, +%.0f/-%.0f" % (len(r0["turns"]), len(r1["turns"]), r0["asc"], r0["dsc"]))
        else: skip("old 4dp v1 (merge rule, smoothing)", "v1 GPX no longer in the repo (optional)")
    guarded(routes)

    def run5k():
        f = find("28_10.fit", "5k_28oct.fit", "30_10.fit")
        if not f: return skip("5K trial tests", "tests/28_10.fit not in the repo (optional)")
        r = cp.run_finish_report(f, show=False); sp = [round(s["time_s"] * 1000 / (s["to_m"] - s["from_m"])) for s in r["splits"]]
        check("5K 28 Oct: km splits 5:04 4:57 4:51 4:35 4:03", all(abs(x - y) <= 1 for x, y in zip(sp, [304, 297, 291, 275, 243])), str([cp.fmt_t(x) for x in sp]))
        check("5K 28 Oct: second half 11.6-11.8% faster", 11.3 < r["halves"]["faster_pct"] < 12.0, "%.1f%%" % r["halves"]["faster_pct"])
        check("5K 28 Oct: HR zones 17% / 68% / 16% (run zones)", abs(r["zones"][2] - 0.17) < 0.02 and abs(r["zones"][3] - 0.68) < 0.02 and abs(r["zones"][4] - 0.16) < 0.02, str([round(x, 2) for x in r["zones"]]))
    guarded(run5k)

    def fourdp():
        f = find("01_11.fit", "4dp_01_11.fit")
        if not f: return skip("4DP report (1 Nov)", "tests/01_11.fit not in the repo (optional)")
        r = cp.fourdp_report(f, show=False); b = r["blocks"]; sp = r["sprints"]
        check("4DP 1 Nov: 5 min 230.8 W, 20 min 183.9 W, 1 min 312.0 W (best windows)", abs(b["5min"]["avg_w"] - 230.8) < 0.5 and abs(b["20min"]["avg_w"] - 183.9) < 0.5 and abs(b["1min"]["avg_w"] - 312.0) < 0.5, "%.1f / %.1f / %.1f W" % (b["5min"]["avg_w"], b["20min"]["avg_w"], b["1min"]["avg_w"]))
        check("4DP 1 Nov: sprints 672 / 686 W, meter consistent with physics", len(sp) == 2 and abs(sp[0]["best5s_w"] - 672) < 2 and abs(sp[1]["best5s_w"] - 686) < 2 and all(0.8 < x["energy"]["ratio"] < 1.25 for x in sp), str([(round(x["best5s_w"]), round(float(x["energy"]["ratio"]), 2)) for x in sp]))
        check("4DP 1 Nov: gap before the 20 min includes a 3:13 stop", abs(r["gaps"]["5min->20min"]["stopped_s"] - 193) <= 3, "%d s stopped" % r["gaps"]["5min->20min"]["stopped_s"])
        h = cp.hour_test_report(f, dur=1200, show=False)
        check("hour_test_report on the 4DP 20 min: 183.9 W, HR 171.9 flat (LTHR estimate)", abs(h["avg_w"] - 183.9) < 0.3 and abs(h["lthr_est"] - 171.9) < 0.3 and abs(h["hr_halves"][0] - h["hr_halves"][1]) < 1, "%.1f W, HR %.1f" % (h["avg_w"], h["lthr_est"]))
    guarded(fourdp)

    def meters():
        f = find("06_11_stages_series.json"); j = find("06_11_kickr_streams.json")
        if not (f and j): return skip("KICKR vs Stages (6 Nov)", "tests/06_11_stages_series.json or tests/06_11_kickr_streams.json not in the repo (optional)")
        import json
        s = json.load(open(f)); ref = {k: np.array([np.nan if v is None else v for v in s[k]], float) for k in ("t", "p", "hr", "cad")}; d = json.load(open(j))
        r1 = cp.meter_offset(ref, cp.stream_series(d["vr1"]["streams"], d["vr1"]["start_local"]), show=False)
        r2 = cp.meter_offset(ref, cp.stream_series(d["vr2"]["streams"], d["vr2"]["start_local"]), show=False)
        check("KICKR vs Stages 6 Nov: MyWhoosh clock -51 s / -2 s, KICKR 6-10% above Stages", abs(r1["lag_s"] + 51) <= 3 and abs(r2["lag_s"]) <= 3 and 1.06 < r1["ratio"] < 1.11 and 1.06 < r2["ratio"] < 1.11,
              "lags %+d / %+d s, ratios %.3f / %.3f" % (r1["lag_s"], r2["lag_s"], r1["ratio"], r2["ratio"]))
        g7, k7 = find("07_11_garmin.fit"), find("07_11_kickr.fit")
        if g7 and k7:
            r7 = cp.meter_offset(cp.fit_series(g7), cp.fit_series(k7), show=False)
            check("KICKR vs Stages 7 Nov (both FITs, 1 Hz): lag -3 s, KICKR about 4% above Stages", abs(r7["lag_s"] + 3) <= 2 and 1.02 < r7["ratio"] < 1.06, "lag %+d s, ratio %.3f" % (r7["lag_s"], r7["ratio"]))
        else: skip("KICKR vs Stages 7 Nov", "tests/07_11_*.fit not in the repo (optional)")
    guarded(meters)

    def digest():
        rc, uc = find("tests/digest_rides_09_11.csv"), find("tests/digest_runs_09_11.csv")
        if not (rc and uc): skip("history digest generator", "tests/digest_*_09_11.csv not in the repo"); return
        out = os.path.join(tmp, "digest.md")
        virt = cp.parse_bests("8min=176@2026-11-04, 10min=177@2026-11-04")
        cp.make_history_digest(rc, uc, out, strava_now=cp.parse_bests("5s=686@2026-11-01, 20min=184@2026-11-01"), strava_virtual=virt,
                               ftp=180, asof="test", export_name="test export")
        t = open(out, encoding="utf-8").read()
        ok = ["Outdoor rides: 46 (33 with power" in t, "Virtual rides (MyWhoosh, KICKR power): 6" in t, "Runs: 7" in t,
              "### Indoor bests" in t, "10min 177 W > 8min 176 W" in t, "| 2026-11-02 | 6 (6 V) |" in t, "| 2026-11-08 | V |" in t,
              "| 20min | 184 | 01 Nov | 184 | 01 Nov |" in t, t.startswith("# History digest: Pat, cycling | running\n")]
        check("history digest (9 Nov CSVs): outdoor/virtual split 46/6, indoor bests with inversion note, V markers, bests table", all(ok), str(ok))
    guarded(digest)

    def virtual_fit_skip():
        import segments_tool as st
        fs = [find("tests/07_11_kickr.fit"), find("tests/07_11_garmin.fit")]
        if not all(fs): skip("segments: indoor FITs skipped", "tests/07_11_*.fit not in the repo"); return
        sub = [st._from_fit_bytes(open(f, "rb").read()).get("sub_sport") for f in fs]
        check("segments: MyWhoosh and Edge indoor FITs are marked indoor (load_rides skips them)", all(x in ("virtual_activity", "indoor_cycling") for x in sub), str(sub))
    guarded(virtual_fit_skip)

    def segment_rules():
        import segments_tool as st
        pr = dict(time_s=69, w=270.3, w_el=270.3)
        ok = [st.is_tracked(dict(time_s=82, w=236, w_el=236.4), pr, -0.2), not st.is_tracked(dict(time_s=83, w=194, w_el=194), pr, -0.2),
              not st.is_tracked(dict(time_s=75, w=280, w_el=180), pr, -0.2),                       # stop inside: elapsed power counts
              st.is_tracked(dict(time_s=74, w=float("nan"), w_el=float("nan")), dict(time_s=69, w=float("nan")), -0.2),
              not st.is_tracked(dict(time_s=76, w=float("nan"), w_el=float("nan")), dict(time_s=69, w=float("nan")), -0.2),   # 1.10 x on the flat
              st.is_tracked(dict(time_s=84, w=float("nan"), w_el=float("nan")), dict(time_s=69, w=float("nan")), 4.2)]        # 1.22 x on a climb
        check("segments: tracking rule (80% of PR power, stops count, time rule without power)", all(ok), str(ok))
        e = lambda **k: {**dict(time_s=45, w=230, hr=135, hr_start=105, hr_end=165), **k}
        fl = [st.hr_flag(e()), st.hr_flag(e(hr_end=72, hr=70, hr_start=70)), st.hr_flag(e(hr_start=141, hr_end=130, hr=137)), st.hr_flag(e(time_s=150, hr=125, hr_end=150)), st.hr_flag(e(w=150, hr=90, hr_end=90)),
              st.hr_flag(e(w=180, time_s=238, hr=106, hr_start=128, hr_end=96)), st.hr_flag(e(hr_cov=0.5))]
        check("segments: HR check (lagging HR ok; low end HR, falling HR, low 2-min avg, 150 W tier, coverage flagged)", fl == ["", "HR?", "HR?", "HR?", "", "HR?", "HR partial"], str(fl))
        u = st.hr_unusable({"hr_unusable": {"1": "bad", "2": {"from_min": 40, "to_min": 58, "note": "x"}}}, dict(key="2", ride_min=50, ride_min_end=52))
        check("segments: rides / minute ranges with unusable HR", u == "x" and st.hr_unusable({"hr_unusable": {"1": "bad"}}, dict(key="1", ride_min=0, ride_min_end=1)) == "bad")
    guarded(segment_rules)

    def segments():
        if not os.path.exists(os.path.join(HERE, "segments.json")): return skip("segments", "segments.json not in the repo")
        if not csv: return skip("segments", "no strava_export_*.zip found")
        import segments_tool as st
        data = st.load_segments(os.path.join(HERE, "segments.json")); seg = {s["id"]: s for s in data["segments"]}
        import gzip
        f = ride("2026-09-27"); raw = open(f, "rb").read(); acts = {"0927": st._from_fit_bytes(gzip.decompress(raw) if f.endswith(".gz") else raw)}
        fp = st.fingerprint(acts, km=1.56, time_s=221, w=248, cad=88, hr=183, hrmax=189, show=False)
        check("segments: fingerprint finds Mount Phantasialand PR on 27 Sep (221 s, 248 W)", fp and fp[0][0] < 3 and abs(fp[0][5] - 248.1) < 0.5, "score %.1f, %.1f W" % (fp[0][0], fp[0][5]) if fp else "none")
        e1 = st.find_efforts(acts, seg[6678444]["ref"]); e2 = st.find_efforts(acts, seg[42273304]["ref"])
        check("segments: 27 Sep Flammgasse 136 s / 270 W; Kierberger 2 efforts 106 s + 69 s (Strava 109 / 69 s)",
              len(e1) == 1 and abs(e1[0]["time_s"] - 136) <= 1 and abs(e1[0]["w"] - 270.3) < 1.5 and len(e2) == 2 and abs(e2[1]["time_s"] - 69) <= 1 and abs(e2[0]["time_s"] - 108) <= 3,
              "%s / %s" % ([round(e["time_s"]) for e in e1], [round(e["time_s"]) for e in e2]))
    guarded(segments)

    n = {k: sum(1 for x in RES if x[0] == k) for k in ("PASS", "FAIL", "SKIP")}
    print("\nSUMMARY: %(PASS)d passed, %(FAIL)d failed, %(SKIP)d skipped" % n)
    return 1 if n["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())

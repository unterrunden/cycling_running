#!/usr/bin/env python3
"""selfcheck.py - regression test of the coaching toolkit (analysis_tools.py, routes_tool.py, cp_lib.py, segments_tool.py, digest_tool.py; 2026-11-28).

Run in a fresh chat after cloning the repo:   pip install fitparse scipy pandas --break-system-packages ; python3 selfcheck.py
It reproduces numbers that were validated against Strava / the chats (20 Sep ride, 22 Sep hour, route geometry, C19 loop, 5K trial, 4DP ...),
so a silent bug introduced by a script change shows up as FAIL. SKIP = the needed data file is not in the repo.
Data (repo folder, data/ or tests/): the newest strava_export_<dd_mm>.zip, every all_routes_*.zip (zips can be replaced by
newer ones with the same name pattern) and the files in tests/ (dd_mm_<name>: FITs, streams and digest CSVs; see README.md).
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

    route_zips = find_all("all_routes_*.zip")
    for k, z in enumerate(route_zips):
        zipfile.ZipFile(z).extractall(os.path.join(tmp, "gpx", str(k)))

    def g(pat):
        hits = glob.glob(os.path.join(tmp, "gpx", "**", pat), recursive=True)
        return hits[0] if hits else None

    def routes():
        if not route_zips: return skip("route tests", "no all_routes_*.zip found")
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
            check("C19: loop only, 16.5 km, closes, +23 m, 4 corners", lc.get("closed") and abs(lc["loop_km"] - 16.5) < 0.2 and abs(lc["loop_asc"] - 23) < 3 and len(r19["turns"]) == 4, "loop %.1f km, +%.0f m, %d turns" % (lc.get("loop_km", 0), lc.get("loop_asc", 0), len(r19["turns"])))
        else: skip("C19 loop closure", "uninterrupted loop GPX not found")
        c1 = g("4dp v2.gpx")
        if c1:
            r0 = rt.analyse(c1); r1 = rt.analyse(c1, merge_km=0.35)
            check("C1 (4dp v2): 55.1 km, 28 raw / 17 merged turns, +166/-168 m (merge rule, smoothing)", abs(r0["km"] - 55.1) < 0.2 and len(r0["turns"]) == 28 and len(r1["turns"]) == 17 and abs(r0["asc"] - 166) < 6 and abs(r0["dsc"] - 168) < 6, "%.1f km, %d / %d turns, +%.0f/-%.0f" % (r0["km"], len(r0["turns"]), len(r1["turns"]), r0["asc"], r0["dsc"]))
        else: skip("C1 geometry (merge rule, smoothing)", "4dp v2.gpx not found in the routes zip")
    guarded(routes)

    def run5k():
        f = find("28_10.fit")
        if not f: return skip("5K trial tests", "tests/28_10.fit not in the repo (optional)")
        r = cp.run_finish_report(f, show=False); sp = [round(s["time_s"] * 1000 / (s["to_m"] - s["from_m"])) for s in r["splits"]]
        check("5K 28 Oct: km splits 5:04 4:57 4:51 4:35 4:03", all(abs(x - y) <= 1 for x, y in zip(sp, [304, 297, 291, 275, 243])), str([cp.fmt_t(x) for x in sp]))
        check("5K 28 Oct: second half 11.6-11.8% faster", 11.3 < r["halves"]["faster_pct"] < 12.0, "%.1f%%" % r["halves"]["faster_pct"])
        old = cp.hr_zone_time(cp.run_series(f)["hr"], [130, 160, 175, 190])
        check("5K 28 Oct: HR zones 14 / 65 / 21% (run zones since 17 Nov: 150/164/173/188; old set 17 / 68 / 16%)",
              abs(r["zones"][2] - 0.14) < 0.02 and abs(r["zones"][3] - 0.65) < 0.02 and abs(r["zones"][4] - 0.21) < 0.02 and abs(old[2] - 0.17) < 0.02 and abs(old[3] - 0.68) < 0.02 and abs(old[4] - 0.16) < 0.02,
              "%s / old %s" % ([round(x, 2) for x in r["zones"]], [round(x, 2) for x in old]))
    guarded(run5k)

    def run_zone_tools():
        v = cp.vdot(5000, 1410); p30, p60 = cp.vdot_pace(v, 30), cp.vdot_pace(v, 60); fz = cp.friel_run_hr_zones(181)
        check("run zones: VDOT 41.2 (23:30 5K), all-out 30 / 60 min 4:45 / 4:56, Friel Z4 at LTHR 181 = 172-180",
              abs(v - 41.2) < 0.1 and abs(p30 - 285) < 2 and abs(p60 - 296) < 2 and fz[3] == ("Z4", 172, 180), "VDOT %.2f, %s / %s, %s" % (v, cp.fmt_t(p30), cp.fmt_t(p60), fz[3]))
        f = find("28_10.fit")
        if f:
            r = cp.run_tt_report(f, show=False)
            check("run_tt_report 28 Oct 5K: HR 181.8 average, 184.1 over the last 20 min, drift about +0.5 bpm/min",
                  abs(r["hr_avg"] - 181.8) < 0.4 and abs(r["hr_last"] - 184.1) < 0.4 and 0.3 < r["drift_bpm_min"] < 0.65, "%.1f / %.1f, %+.2f" % (r["hr_avg"], r["hr_last"], r["drift_bpm_min"]))
        else: skip("run_tt_report 28 Oct", "tests/28_10.fit not in the repo (optional)")
        if not csv: return skip("run HR-pace model and zone fit", "no strava_export_*.zip found")
        df = cp.load_activities_csv(csv); runs = df[df["type"].str.contains("Run") & (df["date"] <= "2026-10-28")]
        bad = {"2026-10-23": [(22, 31)], "2026-10-26": [(17.3, 20.7)]}            # frozen strap values (held HR during stops / 186 s at 181)
        wins = {d: cp.run_hr_pace_windows(cp.run_1hz(os.path.join(act_dir, fn), bad=bad.get(d))) for d, fn in zip(runs["date"], runs["file"])}
        mdl = cp.run_hr_pace_model(wins, exclude=("2026-10-12",))
        W = np.vstack([wins[d] for d in wins if d != "2026-10-12"]); o = cp.run_hr_zone_optimise(W, [386, 333, 299, 280], step=1)
        check("run HR-pace model (6 runs, 12 Oct heat excluded): 6.7 bpm per km/h, HR at 5:00 about 173; zone fit Z2/Z3 161-164, Z4/Z5 183-186",
              sum(len(w) for w in wins.values()) == 162 and abs(mdl["slope"] - 6.68) < 0.1 and abs(mdl["hr_at"](300) - 173) < 1
              and 160 <= o["edges"][1] <= 165 and 183 <= o["edges"][3] <= 186,
              "%d windows, slope %.2f, HR@5:00 %.1f, fit %s (bal %.2f)" % (sum(len(w) for w in wins.values()), mdl["slope"], mdl["hr_at"](300), o["edges"], o["balanced"]))
    guarded(run_zone_tools)

    def fourdp():
        f = find("01_11.fit")
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
        g11, k11 = find("tests/11_11_garmin.fit"), find("tests/11_11_kickr.fit")
        if g11 and k11:
            gs, ks = cp.fit_series(g11), cp.fit_series(k11); t0 = gs["t"][0]; cut = [(t0 + 3678, t0 + 3814)]     # KICKR power cable out (Edge min 61.3-63.6)
            rh = cp.meter_offset(gs, ks, show=False, mask=cut); rp = cp.meter_offset(gs, ks, show=False, align="power", mask=cut)
            ratio = {(row[0], row[1]): row[6] for row in rp["bands"]}       # band rows: (lo, hi, n, other, ref, diff, ratio)
            check("KICKR vs Stages 11 Nov: MyWhoosh HR 4 s behind the Edge (HR lag -4 s), power lag 0 s, KICKR +2% at 120-150 W",
                  abs(rh["lag_s"] + 4) <= 1 and abs(rp["lag_s"]) <= 1 and rp["align"] == "p" and 1.01 < ratio[(120, 150)] < 1.03,
                  "HR lag %+d s, power lag %+d s, 120-150 W ratio %.3f" % (rh["lag_s"], rp["lag_s"], ratio[(120, 150)]))
        else: skip("KICKR vs Stages 11 Nov", "tests/11_11_*.fit not in the repo (optional)")
    guarded(meters)

    def digest():
        rc, uc = find("tests/09_11_digest_rides.csv"), find("tests/09_11_digest_runs.csv")
        if not (rc and uc): skip("history digest generator", "tests/09_11_digest_*.csv not in the repo"); return
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

    def aerobic():
        import numpy as np
        rng = np.random.default_rng(1); p = []; h = []
        for n, w, hr in [(600, 110, 125), (1200, 130, 140), (600, 150, 150), (300, 110, 140), (900, 175, 165), (600, 100, 135)]:
            p += list(w + rng.normal(0, 4, n)); h += list(np.linspace(h[-1] if h else 120, hr, n))
        t = 1.7e9 + np.arange(len(p)); ser = dict(t=t, p=np.array(p), hr=np.array(h), cad=np.full(len(p), 88.0))
        o = dict(t=t + 3, p=np.array(p) * 1.04, hr=np.array(h), cad=np.full(len(p), 88.0))
        r = cp.aerobic_check(ser, other=o, show=False)
        ok = [r[0]["found"] and abs(r[0]["length_s"] - 1200) <= 30 and abs(r[0]["hr_last"] - 136.25) < 0.5, r[1]["found"] and abs(r[1]["avg_w"] - 150) < 1,
              abs(r[0].get("other_ratio", 0) - 1.04) < 0.005, not r[0]["short"]]
        f = find("tests/07_11_kickr.fit")
        if f: ok.append(not cp.aerobic_check(f, show=False)[0]["found"])      # hilly 7 Nov ride: no steady 130 W block
        check("aerobic_check: finds the 130 W / 150 W blocks, HR of the last 10 min, meter ratio; none on a hilly ride", all(ok), str(ok))
        k11, g11 = find("tests/11_11_kickr.fit"), find("tests/11_11_garmin.fit")
        if k11 and g11:
            a = cp.aerobic_check(k11, other=g11, show=False)
            check("aerobic_check 11 Nov (check 0, old fan): 130 W HR 149.6, 150 W HR 160.9, Stages/KICKR 0.979 / 0.991",
                  a[0]["found"] and a[1]["found"] and abs(a[0]["hr_last"] - 149.6) < 0.3 and abs(a[1]["hr_last"] - 160.9) < 0.3
                  and abs(a[0]["other_ratio"] - 0.979) < 0.005 and abs(a[1]["other_ratio"] - 0.991) < 0.005,
                  "HR %.1f / %.1f, ratios %.3f / %.3f" % (a[0]["hr_last"], a[1]["hr_last"], a[0]["other_ratio"], a[1]["other_ratio"]))
        else: skip("aerobic_check 11 Nov", "tests/11_11_*.fit not in the repo (optional)")
    guarded(aerobic)

    def peak_and_docs():
        g11 = find("tests/11_11_garmin.fit")
        if g11:
            r = cp.hr_peak_clean(g11, show=False)
            check("hr_peak_clean 11 Nov: record max 194, clean peak 192.9 / 192.5 bpm (5 / 10 beats), 98.5% clean",
                  r["record_max"] == 194 and abs(r["peak5"] - 192.9) < 0.2 and abs(r["peak10"] - 192.5) < 0.2 and abs(r["clean_pct"] - 98.5) < 0.2,
                  "max %.0f, %.1f / %.1f, %.1f%%" % (r["record_max"], r["peak5"], r["peak10"], r["clean_pct"]))
        else: skip("hr_peak_clean 11 Nov", "tests/11_11_garmin.fit not in the repo (optional)")
        raw = "# A\r\nx\r\n \r\n## B\r\ntext\r\n### C\r\n```\r\n# not a heading\r\n```\r\n \r\n"
        want = "# A\nx\n\n## B\ntext\n\n### C\n```\n# not a heading\n```\n"
        check("normalize_md: CRLF, blank lines with a space, blank line before headings (not inside code fences)", cp.normalize_md(raw) == want)
    guarded(peak_and_docs)

    def cli():
        import subprocess
        f = find("tests/01_11.fit")
        if not f: return skip("analysis_tools CLI", "tests/01_11.fit not in the repo (optional)")
        out = subprocess.run([sys.executable, os.path.join(HERE, "analysis_tools.py"), f], capture_output=True, text=True, timeout=300).stdout
        check("analysis_tools CLI on the 4DP file: runs, FTP default taken from cp_lib.CFG (%.0f W)" % cp.CFG["ftp"], ("At FTP %d W" % cp.CFG["ftp"]) in out, out[:0])
    guarded(cli)

    def hour_test():
        g12, k12 = find("tests/12_11_garmin.fit"), find("tests/12_11_kickr.fit")
        if not (g12 and k12): return skip("hour test 12 Nov", "tests/12_11_*.fit not in the repo (optional)")
        h = cp.hour_test_report(g12, other=k12, show=False)
        check("hour test 12 Nov: 175.1 W Stages, KICKR ratio 1.00, LTHR estimate 173.2, decoupling about +1%",
              abs(h["avg_w"] - 175.1) < 0.2 and abs(h["other_avg_w"] / h["avg_w"] - 1.0) < 0.01 and abs(h["lthr_est"] - 173.2) < 0.3 and 0 < h["decoupling_pct"] < 2.5,
              "%.1f W, ratio %.3f, LTHR %.1f, decoupling %+.1f%%" % (h["avg_w"], h["other_avg_w"] / h["avg_w"], h["lthr_est"], h["decoupling_pct"]))
    guarded(hour_test)

    def meter_checks():
        g11, k11, g12, k12 = find("tests/11_11_garmin.fit"), find("tests/11_11_kickr.fit"), find("tests/12_11_garmin.fit"), find("tests/12_11_kickr.fit")
        if not (g11 and k11 and g12 and k12): return skip("meter_offset checks", "tests/11_11_* or 12_11_*.fit not in the repo (optional)")
        m11 = cp.meter_offset(cp.fit_series(g11), cp.fit_series(k11), align="power", show=False)
        m12 = cp.meter_offset(cp.fit_series(g12), cp.fit_series(k12), align="power", show=False)
        e = m11["erg"]; good = [x["lag_s"] for x in m11["seg"] if x["ok"]]
        check("meter_offset v1.12 (11 / 12 Nov): ERG holds 129.5 / 149.6 W KICKR = ratio 1.02 / 1.01, segment lags 0 s, no warnings; 12 Nov low r confirmed by segments (note only)",
              len(e) == 2 and abs(e[0]["other_w"] - 129.5) < 0.5 and abs(e[0]["ratio"] - 1.022) < 0.005 and abs(e[1]["ratio"] - 1.011) < 0.005
              and good and all(abs(g) <= 1 for g in good) and not m11["warn"] and not m12["warn"] and any("confirm" in x for x in m12["notes"]),
              "ERG %s, segment lags %s, warnings %s / %s" % ([(round(x["other_w"], 1), round(x["ratio"], 3)) for x in e], good, m11["warn"], m12["warn"]))
        # synthetic timer freeze: drop 120 s from the middle of the KICKR file and close the gap (what MyWhoosh does)
        k = cp.fit_series(k11); cut = (k["t"] > k["t"][0] + 3000) & (k["t"] <= k["t"][0] + 3120)
        kf = {x: k[x][~cut] for x in ("t", "p", "hr", "cad")}; kf["t"] = np.where(kf["t"] > k["t"][0] + 3120, kf["t"] - 120, kf["t"])
        mf = cp.meter_offset(cp.fit_series(g11), kf, align="power", show=False)
        check("meter_offset: a synthetic 2-min timer freeze is flagged as piecewise offsets", any("piecewise" in w for w in mf["warn"]), str(mf["warn"]))
    guarded(meter_checks)

    def check1_17_11():
        g, k = find("tests/17_11_garmin.fit"), find("tests/17_11_kickr.fit")
        if not (g and k): return skip("aerobic check #1 17 Nov", "tests/17_11_*.fit not in the repo (optional)")
        a = cp.aerobic_check(k, other=g, show=False); e = cp.erg_blocks(cp.fit_series(g), cp.fit_series(k))
        b150 = [x for x in e if abs(x["other_w"] - 149.6) < 1]
        check("aerobic check #1 17 Nov (v1.14): 130 W block from min 10 (not the later Z2 block), HR 135.1 / 146.4 (Edge), 150 W block Stages about 146.5 W (local alignment)",
              abs(a[0]["start_min"] - 10.0) < 0.5 and abs(a[0]["other_hr_last"] - 135.1) < 0.4 and abs(a[1]["other_hr_last"] - 146.4) < 0.4 and abs(a[1]["avg_w"] - 149.6) < 0.5
              and len(b150) == 1 and abs(b150[0]["ref_w"] - 146.5) < 0.6,
              "start %.1f, HR %.1f / %.1f, 150 W block Stages %s" % (a[0]["start_min"], a[0]["other_hr_last"], a[1]["other_hr_last"], [round(x["ref_w"], 1) for x in b150]))
    guarded(check1_17_11)

    def meters_26_11():
        g, k = find("tests/26_11_garmin.fit"), find("tests/26_11_kickr.fit")
        if not (g and k): return skip("meter_compare 26 Nov", "tests/26_11_*.fit not in the repo (optional)")
        r = cp.meter_compare(g, k, windows=[(1210, 1810)], show=False); w = r["windows"][0]
        check("meter_compare 26 Nov (v1.17): lag path through the MyWhoosh freezes (27 s in the 10-min all-out, about 222 s at the end); Stages 232.3 W, KICKR about 223.5 W",
              abs(w["ref_w"] - 232.3) < 0.2 and 222.5 < w["other_w"] < 224.5 and r["lag"][1500] == 27 and abs(r["lag"][-1] - 222) <= 2,
              "Stages %.1f, KICKR %.1f W, lag %d / %d s" % (w["ref_w"], w["other_w"], r["lag"][1500], r["lag"][-1]))
        kk, f = cp.pd_power_law(600, 232.3, 3600, 175.1)
        check("pd_power_law / pd_predict (v1.17): 10 / 60 min give k -0.158 and 20 min 208 W; CFG CP 185 / W' 28 kJ give 10 min 231.7 W",
              abs(kk + 0.158) < 0.001 and abs(float(f(1200)) - 208.2) < 0.2 and abs(float(cp.pd_predict(600)) - 231.7) < 0.1,
              "k %.3f, 20 min %.1f W, 2P 10 min %.1f W" % (kk, float(f(1200)), float(cp.pd_predict(600))))
    guarded(meters_26_11)

    def wprime():
        f = find("tests/01_11.fit")
        if not f: return skip("W' tools", "tests/01_11.fit not in the repo (optional)")
        a, ex, tl = cp.load_activity(f); P = np.nan_to_num(tl["P"])
        n = cp.wprime_needed(P, 175); w, tau = cp.wbal(P, 175, 18000, "integral")
        fit = cp.pd_fit({120: 279.3, 180: 257.7, 300: 230.8, 480: 202.5, 600: 202.2, 900: 187.4, 1200: 183.9})
        check("W' tools on the 1 Nov 4DP (CP 175): needed 15.2 / 17.5 kJ (integral / differential), 18 kJ leaves 2.8 kJ after the 5 min; 2P fit CP 172 W / W' 15.2 kJ",
              abs(n["integral"] - 15160) < 100 and abs(n["differential"] - 17530) < 150 and abs(w.min() - 2840) < 100 and abs(np.argmin(w) / 60 - 50.5) < 0.3
              and abs(fit["cp"] - 172.4) < 0.2 and abs(fit["wprime"] - 15240) < 100,
              "needed %.1f / %.1f kJ, min %.1f kJ at min %.1f, fit %.1f W / %.1f kJ" % (n["integral"] / 1000, n["differential"] / 1000, w.min() / 1000, np.argmin(w) / 60, fit["cp"], fit["wprime"] / 1000))
    guarded(wprime)

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
        dat = dict(capability=dict(points=[[60, 345], [300, 248], [1200, 184]]), tracking={})
        seg = dict(grade_pct=-0.3); E = lambda t, w: dict(time_s=t, w=w, w_el=w)
        ef = [E(68, 206), E(70, 160), E(75, float("nan"))]                                  # Römersprint-like: PR at 62% of ability
        ef2 = [E(94, 236), E(100, 225), E(110, float("nan")), E(90, float("nan"))]          # Metternich-like: PR at 78%
        cp60 = st.capability(dat, 60); cp300 = st.capability(dat, 300)
        f1 = st.track_flags(ef, seg, dat); f2 = st.track_flags(ef2, dict(grade_pct=8.2), dat)
        f3 = st.track_flags([E(794, 135)], dict(grade_pct=-0.4), dict(capability=dict(points=[[600, 202], [1200, 184]]), tracking={}))
        check("segments v1.5 (22 Nov): ability curve 345 / 248 W; weak PR not tracked (and no-power not faster); 78% PR + 72% tracked, no-power by time; Z2 TT under 90% FTP not tracked",
              cp60 == 345 and cp300 == 248 and f1 == [False, False, False] and f2 == [True, True, True, True] and f3 == [False] and st.track_flags(ef2, dict(track=False), dat) == [False] * 4,
              "%s %s %s %s %s" % (cp60, cp300, f1, f2, f3))
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
        f21 = os.path.join(HERE, "tests", "21_11_garmin.fit")
        if not os.path.exists(f21) or not all(k in seg for k in (7228295, 17985090, 18357516)):
            return skip("segments: 21 Nov efforts", "tests/21_11_garmin.fit or the 22 Nov segments missing")
        a21 = {"21_11": st._from_fit_bytes(open(f21, "rb").read())}
        e3 = st.find_efforts(a21, seg[7228295]["ref"]); e4 = st.find_efforts(a21, seg[17985090]["ref"]); e5 = st.find_efforts(a21, seg[18357516]["ref"])
        check("segments (22 Nov): 21 Nov Erp-Friesheim 303 s / 156 W and Knallgas runter 62 s (Strava 303 s / 156.3 W, 62 s); Romersprint ridden in reverse = no effort",
              len(e3) == 1 and abs(e3[0]["time_s"] - 303) <= 1 and abs(e3[0]["w"] - 156.3) < 1.5 and len(e4) == 1 and abs(e4[0]["time_s"] - 62) <= 1 and not e5,
              "%s / %s / %d" % ([(round(e["time_s"]), round(e["w"], 1)) for e in e3], [round(e["time_s"]) for e in e4], len(e5)))
    guarded(segments)

    def tools_v3():
        f22 = os.path.join(HERE, "tests", "22_11_garmin.fit")
        if not os.path.exists(f22): return skip("tools v3 (22 Nov)", "tests/22_11_garmin.fit not in the repo")
        import routes_tool as rt, analysis_tools as at
        fac = rt.calibrate_time(f22, 131.3, 12973)
        check("routes_tool v3: time model on the 22 Nov ride (86.9 km track, 131.3 W, 216:13 moving) -> factor 1.049 (21 Nov: 1.043; TIME_FACTOR 1.046)",
              abs(fac - 1.049) < 0.004 and abs(rt.TIME_FACTOR - 1.046) < 1e-9, "%.4f" % fac)
        r = at.long_ride_report(f22, show=False)
        check("analysis_tools v3: long-ride report 22 Nov: 86.5 km, NP 143, TSS 241, 29 stops (44:29), finish 17:17 (+39 min vs sunset), decoupling -4.1",
              abs(r["load"]["km"] - 86.5) < 0.1 and abs(r["load"]["np_w"] - 143) < 1 and abs(r["load"]["tss"] - 240.5) < 1.5 and len(r["stops"]) == 29
              and r["elapsed_s"] - r["moving_s"] == 2669 and r["finish"] == "17:17" and r["min_after_sunset"] == 39 and abs(r["dec"]["dec"] + 4.1) < 0.15,
              "%.1f km NP %.0f TSS %.0f stops %d (%d s) %s %+d dec %.1f" % (r["load"]["km"], r["load"]["np_w"], r["load"]["tss"], len(r["stops"]), r["elapsed_s"] - r["moving_s"], r["finish"], r["min_after_sunset"], r["dec"]["dec"]))
        import segments_tool as st
        on = st.on_route(f22); names = {n: d for k, n, d in on}
        check("segments_tool v1.5: on_route of the 22 Nov ride: No10 revers and Metternich Climb forward, Otto-Wels-Sprint and Erp-Friesheim in reverse",
              names.get("No10 revers") == "fwd" and names.get("Metternich Climb") == "fwd" and names.get("Otto-Wels-Sprint") == "rev" and names.get("Erp-Friesheim") == "rev", str(on[:6]))
    guarded(tools_v3)

    def doc_check():
        import cp_lib as cp
        r = cp.doc_token_check("FTP 175 W [Pat 12 Nov]; sunset 16:38; id 21059503183", "FTP 175 W; sunset 16:38", show=False)
        check("cp_lib v1.16: doc_token_check finds the dropped number and tag", r["numbers"] == ["12", "21059503183"] and r["tags"] == ["[Pat 12 Nov]"], str(r))
    guarded(doc_check)

    def metrics_synthetic():
        import cp_lib as cp
        n = 3600; x = dict(P=np.full(n, 175.0), H=np.full(n, 150.0), C=np.full(n, 85.0), D=np.linspace(0, 36000, n), V=np.full(n, 10.0), mov=np.ones(n, bool))
        L = cp.ride_load(x, 175.0)
        check("metrics: 1 h at FTP -> NP 175, IF 1.00, TSS 100, easy 0 %", abs(L["np_w"] - 175) < 1e-6 and abs(L["tss"] - 100) < 0.1 and L["easy_pct"] == 0, "%.2f" % L["tss"])
        r = dict(x, V=np.full(n, 1000 / 300.0), D=np.linspace(0, 12000, n)); Lr = cp.run_load(r, 300.0)
        check("metrics: 1 h at threshold pace -> rTSS 100", abs(Lr["tss"] - 100) < 0.5 and abs(Lr["IF"] - 1) < 0.01, "%.1f" % Lr["tss"])
        import pandas as pd
        P = cp.pmc({d.strftime("%Y-%m-%d"): 100.0 for d in pd.date_range("2026-01-01", periods=400)}, "2026-01-01", "2027-02-04")
        check("metrics: PMC of a constant 100 TSS/day -> CTL and ATL about 100", abs(P.ctl.iloc[-1] - 100) < 0.5 and abs(P.atl.iloc[-1] - 100) < 0.1)
        h = np.concatenate([np.full(1950, 140.0), np.full(1650, 147.0)]); d = cp.aero_decoupling(dict(x, P=np.full(n, 130.0), H=h), "ride", 175.0)
        check("metrics: decoupling of a 5% HR rise at steady power -> +5.0% (unflagged)", abs(d["dec"] - 5.0) < 0.2 and d["dec_flag"] == "", "%.2f %s" % (d["dec"], d["dec_flag"]))
        P2 = np.concatenate([np.full(600, 120.0), np.full(120, 260.0), np.zeros(300), np.full(600, 120.0)]); m = len(P2); tt = np.arange(m, dtype=float)
        H2 = np.where(tt < 600, 135.0, np.where(tt < 720, 135 + 50 * (1 - np.exp(-(tt - 600) / 30)), 0)); pk = 135 + 50 * (1 - np.exp(-120 / 30))
        H2 = np.where(tt >= 720, 100 + (pk - 100) * np.exp(-(tt - 720) / 45), H2)
        ev = cp.hrr_events(dict(P=P2, H=H2, V=np.full(m, 8.0), mov=np.ones(m, bool)), "ride", 175.0)
        exp_drop = (pk - 100) * (1 - np.exp(-60 / 45))
        check("metrics: HRR finds one recovery after a 2-min effort (peak in Z5 -> max)", len(ev) == 1 and ev[0][3] == "max" and abs(ev[0][2] - exp_drop) < 2, str([(round(e[1]), round(e[2], 1), e[3]) for e in ev]))
        check("metrics: score scale anchors (P50 75, P10 55, P90 88, P97.5 93)", [cp.scale_score(p) for p in (50, 10, 90, 97.5)] == [75, 55, 88, 93])
        check("metrics: HCI context of the reference session is 0", abs(cp.hci_context(dict(temp=18, fancat="out", feel=5, atl=35, rpe=np.nan), dict(t_c=0.4, nofan=10, oldfan=7, feel_d=0.2, atl_d=-0.03, rpe_dev=2), (0, 0, 0))[0]) < 1e-9)
        y = np.linspace(0, 1, 200); f1 = cp.lowpass2(np.r_[np.zeros(10), np.ones(190)], 20, 60)
        check("metrics: HR model lag rises with t_on 20 s (63% after 20 s)", abs(f1[30] - (1 - (1 - 1 / 20) ** 21)) < 0.02, "%.3f" % f1[30])
    guarded(metrics_synthetic)

    def digest_v2():
        exp = sorted(find_all("strava_export_*.zip"))
        if not exp or not find("session_context.csv"): return skip("digest_tool", "export zip or data/session_context.csv missing")
        import digest_tool as dg, tempfile, json
        need = [f for f in ("14_11_garmin.fit", "15_11_garmin.fit", "18_11_garmin.fit", "20_11_garmin.fit") if not find(f)]
        if need: return skip("digest_tool", "chat FITs missing in tests/: " + ", ".join(need))
        tmp = tempfile.mkdtemp(); out = os.path.join(tmp, "digest.md")
        M, S, P, B = dg.main(["--root", HERE, "--export", find_all("strava_export_09_11.zip")[0] if find_all("strava_export_09_11.zip") else exp[0],
                              "--out", out, "--tables", tmp, "--asof", "2026-11-20", "--quiet", "--no-sync"])
        g = lambda d, col: float(M[(M.date == d)][col].iloc[0])
        bd = lambda d, col: float(B[B.date == d][col].max())
        check("digest_tool: bests 1 Nov 5 s 685.6 W, 22 Sep 60 min stops excl. 170.0 W", abs(bd("2026-11-01", "el_5s") - 685.6) < 0.2 and abs(bd("2026-09-22", "ro_60min") - 170.0) < 0.1,
              "%.1f / %.1f" % (bd("2026-11-01", "el_5s"), bd("2026-09-22", "ro_60min")))
        check("digest_tool: indoor Stages 20 Nov 30 s 449.0 W, 12 Nov 60 min 175.1 W", abs(bd("2026-11-20", "el_30s") - 449.0) < 0.2 and abs(bd("2026-11-12", "el_60min") - 175.1) < 0.1)
        check("digest_tool: 12 Nov hour test NP 175.5 W, TSS 100.5 (FTP 175)", abs(g("2026-11-12", "np_w") - 175.5) < 0.1 and abs(g("2026-11-12", "tss") - 100.5) < 0.3, "%.1f" % g("2026-11-12", "tss"))
        check("digest_tool: 22 Sep TSS 109 at FTP 170 (NP 177.7)", abs(g("2026-09-22", "tss") - 109.2) < 0.5, "%.1f" % g("2026-09-22", "tss"))
        ref = json.load(open(find("hci_reference.json"))); h = S[(S.flag.fillna("") == "") & (S.date <= ref.get("calibrated", "2026-11-20"))].HCI.dropna()
        check("digest_tool: HCI of the reference sessions has median 75, P10 about 55, P90 about 88", abs(h.median() - 75) < 1 and abs(h.quantile(.1) - 55) < 3 and abs(h.quantile(.9) - 88) < 3 and len(h) == ref["n"],
              "median %.1f P10 %.1f P90 %.1f n %d" % (h.median(), h.quantile(.1), h.quantile(.9), len(h)))
        check("digest_tool: 11 Nov HR max 194 survives the cleaning; 17 Oct (strap) has no HCI", g("2026-11-11", "hr_max") == 194 and S[S.date == "2026-10-17"].flag.iloc[0] == "-")
        txt = open(out, encoding="utf-8").read()
        check("digest_tool: digest has sections 0-8 and the split per-ride tables 5a / 5b", all(("## %d." % i) in txt for i in range(9)) and "### 5a." in txt and "### 5b." in txt)
    guarded(digest_v2)

    n = {k: sum(1 for x in RES if x[0] == k) for k in ("PASS", "FAIL", "SKIP")}
    print("\nSUMMARY: %(PASS)d passed, %(FAIL)d failed, %(SKIP)d skipped" % n)
    return 1 if n["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())

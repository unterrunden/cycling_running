#!/usr/bin/env python3
"""selfcheck.py - regression test of the coaching toolkit (analysis_tools.py, routes_tool.py, cp_lib.py).

Run in a fresh chat after cloning the repo:   pip install fitparse scipy pandas --break-system-packages ; python3 selfcheck.py
It reproduces numbers that were validated against Strava / the first chats (20 Sep ride, 22 Sep hour, 4DP loop geometry, C19 loop, 5K trial ...),
so a silent bug introduced by a script change shows up as FAIL. SKIP = the needed data file is not in the repo.
Data: strava_export_27_10.zip and rides_runs_gpx_files_31_10.zip in the repo folder (or in data/); optional 5K FIT: 5k_28oct.fit or 30_10.fit (repo folder, data/ or tests/).
"""
import os, sys, glob, zipfile, tempfile, traceback
from datetime import date
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
RES = []


def find(*names):
    for base in (HERE, os.path.join(HERE, "data"), os.path.join(HERE, "tests")):
        for n in names:
            p = os.path.join(base, n)
            if os.path.exists(p): return p
    return None


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
    exp = find("strava_export_27_10.zip"); gz = find("rides_runs_gpx_files_31_10.zip")
    act_dir = csv = None
    if exp:
        zipfile.ZipFile(exp).extractall(os.path.join(tmp, "exp")); act_dir = os.path.join(tmp, "exp"); csv = os.path.join(act_dir, "activities.csv")

    def csv_loader():
        df = cp.load_activities_csv(csv); t = cp.csv_totals(df)
        check("activities.csv: 43 rides / 1259.4 km, 6 runs / 33.0 km", len(df) == 49 and t["Ride"]["n"] == 43 and abs(t["Ride"]["km"] - 1259.4) < 0.2 and t["Run"]["n"] == 6 and abs(t["Run"]["km"] - 33.0) < 0.2, str({k: v for k, v in t.items() if k != "gear_km"}))
    if csv: guarded(csv_loader)
    else: skip("activities.csv loader", "strava_export_27_10.zip not found")

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
        check("fit_laps / fit_pauses: tables", len(cp.fit_laps(f20)) >= 1 and len(cp.fit_pauses(f20)) >= 0)
    if csv: guarded(rides)
    else: skip("ride tests (20/22/19 Sep)", "strava_export_27_10.zip not found")

    def routes():
        if not gz: return skip("route tests", "rides_runs_gpx_files_31_10.zip not found")
        zipfile.ZipFile(gz).extractall(os.path.join(tmp, "gpx")); g = lambda pat: glob.glob(os.path.join(tmp, "gpx", "**", pat), recursive=True)[0]
        v1 = g("*3316196558*"); r0 = rt.analyse(v1); r1 = rt.analyse(v1, merge_km=0.35)
        check("4dp v1: 19 raw / 17 merged turns, longest straight 10.1 km", len(r0["turns"]) == 19 and len(r1["turns"]) == 17 and abs(r0["longest_km"] - 10.1) < 0.2, "%d / %d / %.1f km" % (len(r0["turns"]), len(r1["turns"]), r0["longest_km"]))
        check("4dp v1: ascent / descent +152 / -162 m (edge-padded smoothing)", abs(r0["asc"] - 152) < 6 and abs(r0["dsc"] - 162) < 6, "+%.0f / -%.0f" % (r0["asc"], r0["dsc"]))
        lc = rt.loop_closure(g("*uninterrupted loop*"))
        check("C19: loop joins at km 5.3, 16.4 km, +23/-21 m", lc.get("closed") and abs(lc["join_km"] - 5.3) < 0.2 and abs(lc["loop_km"] - 16.4) < 0.2 and abs(lc["loop_asc"] - 23) < 3, str({k: (round(float(v), 1) if not isinstance(v, (bool, tuple)) else v) for k, v in lc.items()}))
        st = rt.stretches(r0, 2.5)
        check("4dp v1: 8.9 km south stretch (km 25.1-34.0, 179 deg)", any(abs(x["L"] - 8.9) < 0.3 and abs(x["hd"] - 179) < 4 for x in st))
    guarded(routes)

    def run5k():
        f = find("5k_28oct.fit", "30_10.fit")
        if not f: return skip("5K trial tests", "5k_28oct.fit / 30_10.fit not in the repo (optional)")
        r = cp.run_finish_report(f, show=False); sp = [round(s["time_s"] * 1000 / (s["to_m"] - s["from_m"])) for s in r["splits"]]
        check("5K 28 Oct: km splits 5:04 4:57 4:51 4:35 4:03", all(abs(x - y) <= 1 for x, y in zip(sp, [304, 297, 291, 275, 243])), str([cp.fmt_t(x) for x in sp]))
        check("5K 28 Oct: second half 11.6-11.8% faster", 11.3 < r["halves"]["faster_pct"] < 12.0, "%.1f%%" % r["halves"]["faster_pct"])
        check("5K 28 Oct: HR zones 17% / 68% / 16% (run zones)", abs(r["zones"][2] - 0.17) < 0.02 and abs(r["zones"][3] - 0.68) < 0.02 and abs(r["zones"][4] - 0.16) < 0.02, str([round(x, 2) for x in r["zones"]]))
    guarded(run5k)

    n = {k: sum(1 for x in RES if x[0] == k) for k in ("PASS", "FAIL", "SKIP")}
    print("\nSUMMARY: %(PASS)d passed, %(FAIL)d failed, %(SKIP)d skipped" % n)
    return 1 if n["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())

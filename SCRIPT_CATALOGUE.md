# Script catalogue

Where the commands of chats 1-3 went. Chats 1-2 (sections up to 10 Nov): source Pat's archive `all_accessible_commands_with_outputs.zip` (87 files, commands up to 1 Nov 13:18; one duplicate removed, hours zero-padded). The archive is not needed in the repo: this file records every disposition. Chat 3 (10-12 Nov, own section below): listed by Claude from its own session (script files and inline commands), so no export is needed.

Only `bash` commands are in the archive (the commands menu in the app); file-creation calls, Strava / web calls and memory calls are not. File names follow `dd_mm.hh_mm[.index]`.

Categories: PORTED = the useful part now lives in the repo (module and function named); SUPERSEDED = replaced by a better version; PATTERN = document-edit technique, now `cp_lib.Patch`; ONE-OFF = analysis of one session or a one-time edit (results live in the notes, the code is not worth keeping); HOUSEKEEPING = `ls` / `unzip` / checks; DUPLICATE / EMPTY.

Counts: PORTED 29, SUPERSEDED 4, PATTERN 6, ONE-OFF 19, HOUSEKEEPING 26, DUPLICATE 2, EMPTY 1 (total 87).

| File | Category | Where it went / why |
|---|---|---|
| `01_10.19_50.1` | HOUSEKEEPING | listing of uploads / zip |
| `01_10.19_50.2` | HOUSEKEEPING | directory setup, unzip |
| `01_10.19_50.3` | SUPERSEDED | `parse.py`: Strava GPX regex parser (power/HR/cad/temp) → `analysis_tools.load_gpx` / `load_fit` |
| `01_10.19_50.4` | SUPERSEDED | `analyze.py`: ride summary (timeline, mean-max, NP, zones) → `analysis_tools.ride_report` / `ride_metrics` |
| `01_10.19_50.5` | PORTED | `analyze2.py`: moving-time curves → `analysis_tools.curves` ('rolling'); decoupling → `cp_lib.decoupling` |
| `01_10.19_50.6` | SUPERSEDED | `route.py`: first route geometry (turns, headings) → `routes_tool.analyse` |
| `01_10.19_50.7` | PORTED | `route2.py`: wind component per stretch → `routes_tool.wind_rel` / `stretches`; best-window distance and speed → `cp_lib.best_window` |
| `01_10.19_50.8` | PORTED | `route3.py`: 25 m grid, 100 m windows, 55° turns, merge within 350 m → `routes_tool.analyse(merge_km=0.35)` (explains 17 vs 19 turns on the 4DP loop) |
| `02_10.06_52.1` | HOUSEKEEPING | directory listing |
| `02_10.06_52.2` | PORTED | `analyze3.py`: 10-min block table, best N-min windows with HR → `cp_lib.ride_blocks` / `best_window` |
| `03_10.10_35` | ONE-OFF | route3 run on the 4DP loop + elevation profile print → `routes_tool` CLI |
| `03_10.19_41.1` | HOUSEKEEPING | head of a GPX file |
| `03_10.19_41.2` | PORTED | `run.py`: GPX run analysis (splits, gaps, HR steps, fastest windows) → `analysis_tools.run_report` + `cp_lib` run tools |
| `03_10.19_41.3` | PORTED | aero model (brentq power → speed) → `cp_lib.speed_from_power` (71 kg / CdA 0.40 then; now 68 kg / 0.38 via CFG since 12 Nov, 72 kg before) |
| `07_10.22_23.1` | HOUSEKEEPING | directory listing |
| `07_10.22_23.2` | PORTED | `kroute.py`: komoot GPX analysis → `routes_tool.analyse` / `stretches`. Not ported: komoot's planned time and speed per km (small, can be added) |
| `08_10.21_56.1` | HOUSEKEEPING | file check |
| `08_10.21_56.2` | PORTED | `today.py`: single-ride session summary (efforts, blocks, HR vs power, decoupling) → `cp_lib.ride_session` |
| `08_10.21_56.3` | ONE-OFF | follow-up query: HR by power band → `cp_lib.hr_by_power` |
| `13_10.10_12.1` | HOUSEKEEPING | file check |
| `13_10.10_12.2` | PORTED | `run2.py`: run analysis v2 → `analysis_tools.run_report`, `cp_lib.fastest_windows` / `hr_steps` |
| `15_10.10_24.1` | HOUSEKEEPING | file check |
| `15_10.10_24.2` | PORTED | `run3.py`: split at recording gaps, rep detection → `cp_lib.fastest_windows`; gap handling in `analysis_tools` |
| `17_10.14_03` | ONE-OFF | 16 Oct ride (HR flat-lines, thirds) → `analysis_tools.ride_report` + `cp_lib.hr_plateaus` |
| `17_10.14_03.1` | DUPLICATE | identical to 17_10.14_03 |
| `17_10.23_11` | ONE-OFF | 17 Oct ride analysis; superseded by `ride_report` / `ride_session` |
| `18_10.12_50` | HOUSEKEEPING | listing of uploads |
| `18_10.21_57.1` | ONE-OFF | 18 Oct partial 5K: cumulative time at distance, laps → `cp_lib.split_table` / `halves` |
| `18_10.21_57.2` | ONE-OFF | loop length from return-to-start → `cp_lib.loop_length` |
| `25_10.20_24.1` | ONE-OFF | weekly volume table from a hard-coded ride list → `cp_lib.weekly_table_md` / `make_history_digest` |
| `25_10.20_24.2` | HOUSEKEEPING | listing of skills / uploads |
| `26_10.09_45.1` | ONE-OFF | usage example of `analysis_tools` v1 (16 Oct file) → README cookbook |
| `26_10.09_45.2` | ONE-OFF | usage example of `analysis_tools` v1 (18 Oct file) → README cookbook |
| `26_10.09_45.3` | PATTERN | patch that extended `analysis_tools` v1 (run report); v2 contains the result |
| `26_10.23_55` | PATTERN | bulk edit of `handoff_brief.md` (11.6 KB); brief replaced by `coach_notes.md`; pattern → `cp_lib.Patch` |
| `28_10.20_22.1` | HOUSEKEEPING | word counts of knowledge files |
| `28_10.20_22.2` | HOUSEKEEPING | reading part of the brief |
| `29_10.01_30.1` | HOUSEKEEPING | reading part of the brief |
| `29_10.01_30.2` | PORTED | `sun()`: NOAA sunrise/sunset → `cp_lib.sun_times` (now DST-aware, minute rounding fixed) |
| `29_10.08_35` | PATTERN | `edit(path, pairs)` with assertions and a fails list → `cp_lib.Patch` |
| `30_10.09_50` | HOUSEKEEPING | first look at `activities.csv` |
| `30_10.09_50.1` | DUPLICATE | identical to 30_10.9_50 |
| `30_10.09_50.2` | PORTED | parse `activities.csv` with duplicated headers → `cp_lib.load_activities_csv` |
| `30_10.09_50.3` | PORTED | CSV vs brief appendix cross-check, UTC → Berlin → `cp_lib.load_activities_csv` / `csv_totals` |
| `30_10.09_50.4` | ONE-OFF | CSV coverage and weekly checks → `cp_lib.csv_totals` / `weekly_table_md` |
| `30_10.12_22.1` | HOUSEKEEPING | zip listing |
| `30_10.12_22.2` | HOUSEKEEPING | GPX zip listing |
| `30_10.16_49.1` | HOUSEKEEPING | sandbox setup (copy script, unzip, pip install fitparse) → README setup line |
| `30_10.16_49.2` | PORTED | FIT message inventory → `cp_lib.fit_inspect` |
| `30_10.16_49.3` | PORTED | FIT record / developer fields → `cp_lib.fit_inspect` |
| `30_10.16_49.4` | PORTED | Garmin ride FIT structure (laps, events, hrv, session) → `fit_inspect` / `fit_laps` / `fit_events` / `fit_pauses` / `hrv_quality` |
| `30_10.16_49.5` | ONE-OFF | patch builder that produced `analysis_tools` v2 (12.9 KB); the result is `analysis_tools.py` v2 itself |
| `31_10.12_50.1` | EMPTY | blank command |
| `31_10.12_50.2` | PORTED | 5K finish analysis (raw HR at the end, plateaus, halves, tail paces) → `cp_lib.run_finish_report` / `tail_paces` / `halves` / `hr_plateaus` |
| `31_10.12_50.3` | PORTED | weekly zone table → `cp_lib.weekly_table_md` |
| `31_10.12_50.4` | PORTED | per-ride table, max-HR check → `cp_lib.make_history_digest` |
| `31_10.12_50.5` | PORTED | 500 m splits and HR zone time → `cp_lib.split_table` / `hr_zone_time` |
| `31_10.12_50.6` | SUPERSEDED | first `routes_tool.py` (had the edge-padding bug) → `routes_tool` v2 |
| `31_10.12_50.7` | PORTED | elevation diagnostics (NaN / jumps) → `routes_tool.elevation_diag` |
| `31_10.12_50.8` | PORTED | edge-padding fix → included in `routes_tool` v2 |
| `31_10.12_50.9` | PORTED | route list with stretches and headings → `routes_tool.stretches` / CLI |
| `31_10.12_50.10` | PORTED | turn lists for key routes → `routes_tool.analyse` |
| `31_10.12_50.11` | PORTED | `history_digest.md` writer → `cp_lib.make_history_digest` (now with post-archive bests in the table) |
| `31_10.12_50.12` | HOUSEKEEPING | date / time check |
| `31_10.12_50.13` | PORTED | `routes_and_courses` entry generator → `routes_tool.route_entry_md` (the per-route notes dictionary was one-off) |
| `31_10.12_50.14` | ONE-OFF | patch of the routes markdown |
| `31_10.12_50.15` | ONE-OFF | creation of `handoff_update_31oct.md` |
| `31_10.12_50.16` | ONE-OFF | check of 135 W share and long-duration dates |
| `31_10.12_50.17` | ONE-OFF | correction patch of the handoff update |
| `31_10.13_16` | HOUSEKEEPING | Project folder listing (memory chat) |
| `31_10.13_29` | HOUSEKEEPING | Project folder listing (memory chat) |
| `31_10.18_10.1` | HOUSEKEEPING | version check of `analysis_tools` in Project |
| `31_10.18_10.2` | PATTERN | `coach_notes` edits (memory chat) → `cp_lib.Patch` |
| `31_10.18_30` | PATTERN | `coach_notes` edits (memory chat) → `cp_lib.Patch` |
| `31_10.18_45` | HOUSEKEEPING | Project / uploads listing |
| `31_10.23_35.1` | PORTED | implied-headwind model, 20-min distance table, CP sketches, C19 loop closure → `cp_lib` physics + `routes_tool.loop_closure` |
| `31_10.23_35.2` | ONE-OFF | patch of the routes markdown (C19, C1) |
| `31_10.23_35.3` | ONE-OFF | wording patch |
| `31_10.23_35.4` | HOUSEKEEPING | diff of Project copies |
| `01_11.00_25` | PORTED | `git clone` of the public repo → README setup |
| `01_11.12_27.1` | HOUSEKEEPING | md5 comparison of repo vs uploads, zip diff |
| `01_11.12_27.2` | PORTED | compare v1 / v2 geometry and moderate bends → `routes_tool.compare_routes` / `moderate_bends` |
| `01_11.12_27.3` | HOUSEKEEPING | Project listing |
| `01_11.12_27.4` | PATTERN | multi-file patch of `coach_notes` / mirror / digest → `cp_lib.Patch` |
| `01_11.12_27.5` | ONE-OFF | routes markdown patch (C1b) |
| `01_11.12_27.6` | HOUSEKEEPING | verification of changed lines |
| `01_11.13_18` | ONE-OFF | comparison of the new 4dp v2 draft; covered by `compare_routes` |

## After the archive (1-5 Nov, chat 2)
- Library build: `cp_lib.py` v1, `routes_tool.py` v2 (merge rule, edge-padded smoothing, comparison, loop closure, entries) and `selfcheck.py`.
- 4DP analysis of 1 Nov → `cp_lib.fourdp_report`, `cp_lib.top_windows`, `cp_lib.sprint_energy_check`; mapping ride GPS onto a route was done ad hoc (candidate for a later helper).
- Routes of 5 Nov: komoot route exports use `<rtept>` instead of `<trkpt>` → `routes_tool.parse` reads both; duplicate detection by point coverage was ad hoc (candidate for a later helper).
- Digest: `cp_lib.make_history_digest` gained post-archive month rows and an "after the archive" section; `cp_lib.index` prints full first sentences.
- `selfcheck.py` picks the newest `strava_export_*.zip` / `all_routes_*.zip` and has optional 5K and 4DP tests.

## 6 Nov (chat 2)
- Segments → `segments_tool.py` v1 + `segments.json`: PR fingerprint search (exact elapsed time, distance, W, cadence, HR avg/max), reference lines, effort finder (start/end within 40 m, course within 40 m, direction check, latest start crossing), archive and markdown. Validated against Strava's efforts of 27 Sep (0-3 s, about 1 W). The two PRs without power were placed by elevation and effort count, one confirmed by Strava's segment list of 20 Aug.
- KICKR vs Stages → `cp_lib.fit_series`, `cp_lib.stream_series`, `cp_lib.meter_offset` (HR cross-correlation alignment, power bands, linear fit); test files `tests/06_11_stages_series.json` + `tests/06_11_kickr_streams.json` (no GPS: the trainer file would show Pat's home).
- Climb physics check of the Stages (meter energy vs m·g·h + drag + kinetic energy on segment efforts): ad hoc, results in `segments.md` (candidate for a later helper).
- `cp_lib.hrv_quality`: junk RR values > 3 s are left out of the time axis (the 6 Nov file spread a 38-min ride over 220 "minutes").

## 7 Nov (chat 2)
- Segment tracking (Pat): only efforts with elapsed-based power >= 80% of the PR effort's power (time rule without power: 1.25 x on climbs, 1.08 x elsewhere) → `segments_tool.is_tracked`; rides with unusable HR (`hr_unusable` in `segments.json`, 17 Oct per Pat, 10 Sep min 40-58) → `segments_tool.hr_unusable`; HR artefact check by end-of-effort HR → `segments_tool.hr_flag`.
- Whole-ride strap check → `cp_lib.hr_artefact_scan` (found 10 Sep min 42-58 and 29 Sep min 56-57, besides 17 Oct).
- HR-zone fit against power zones (steady windows, balanced accuracy, grid search, bootstrap by ride) → `cp_lib.hr_power_windows`, `cp_lib.hr_zone_score`, `cp_lib.hr_zone_optimise`; regression of HR on power with ride fixed effects (0.40 bpm/W within rides, 0.8 bpm/°C between rides) was ad hoc.
- Hour-test analysis prepared → `cp_lib.hour_test_report`.

## 8 Nov (chat 2)
- Segments: 3 more attempted (Liblarer->Bleibtreu See, Fischenich Berg Gleise -> Ampel, Fischenich Berg; fingerprints 0.2-1.6) and 20 to-do climbs with an internal elevation check (grade x length vs difference); `hr_flag` gained a 150 W / 2 min tier and "HR partial" (coverage); `hr_unusable` now holds 17 Oct, 10 Sep min 13-58, 5 Sep min 20-36, 29 Sep min 54-58.
- `cp_lib.hr_artefact_scan` gained the 150 W / 2 min tier and ignores the first 5 min; new `cp_lib.hr_gaps` (missing HR while riding).
- 7 Nov KICKR vs Stages from both FITs (`meter_offset`): +4%, zero offset without effect, +8% at cadence below 60 (ad hoc cadence binning).
- HR-zone variants scored against power zones with Z4 = 90-110% FTP and against the HR of best 2-20 min efforts (ad hoc).

## 9 Nov (chat 2, Strava export of 9 Nov)
- `cp_lib.make_history_digest` rewritten for outdoor vs virtual rides (indoor bests table from the VirtualRide bests, V marker in the weekly and per-ride tables, HR notes per ride, computed counts and no-power dates, automatic note when a longer duration beats a shorter one, section 8 "After the export"); `cp_lib.weekly_table_md` counts indoor rides (cp_lib v1.4).
- `segments_tool.py` v1.3: `_from_fit_bytes` reads sport / sub_sport and `load_rides` skips indoor FITs (07_11_kickr.fit had been loaded as an outdoor ride on its virtual Belgian GPS); the stop flag shows the elapsed-based W, which is what Strava reports for an effort with an auto-paused stop.
- `selfcheck.py`: digest-generator test on `tests/09_11_digest_*.csv`; indoor-FIT skip test (35 checks).
- Ad hoc: 191 bpm (29 Sep) confirmed as the highest strap HR in all files.

## 10 Nov (chat 2)
- Progress checks for the 6-week plan → `cp_lib.aerobic_check` (cp_lib v1.5): finds the 130 W / 150 W blocks of the aerobic check in a ride file, HR of the last 10 / 5 min, drift, W/HR, optional second recording for the meter ratio; selfcheck test on synthetic data plus the hilly 7 Nov file (no block). The other checks use existing tools (`ride_session` decoupling, `run_series` / `split_table`).
- `selfcheck.py`: the old 4DP v1 route test (its GPX is no longer in the repo, so it was always skipped) is replaced by the same merge-rule and smoothing check on C1 (4dp v2: 28 / 17 turns, +166/-168 m); the support branch for the old C19 file (approach + loop), the old `rides_runs_gpx_files_*.zip` pattern and old test-file names (`5k_28oct.fit`, `4dp_01_11.fit`) are removed. 37 checks, none skipped with the current zips.

## Chat 3 (10-12 Nov)
Listed by Claude from the session itself (named = script file in the sandbox scratchpad, inline = a one-off `python3 - <<EOF` or shell command). Counts: PORTED 3, SUPERSEDED 1, ONE-OFF 3, PATTERN 2, HOUSEKEEPING 9 (18 commands; the Strava calls are not counted).

| Command (date) | Category | Where it went / why |
|---|---|---|
| inline: clone + install + selfcheck (10 Nov, twice) | HOUSEKEEPING | first blocked by the session's permission check (code from an external source) until Pat confirmed in the chat; then 37 passed |
| inline: clone into the scratchpad, version and tests/ listing (10 Nov) | HOUSEKEEPING | checked cp_lib v1.5 and the 10 Nov commit |
| `run_10_11.py` (10 Nov) | ONE-OFF | 10 Nov run from a 250-point Strava stream copied by hand: stops (gaps > 30 s), pace per lap and km on a moving clock, HR valid only after the strap was re-attached, a GPS jump after stop 1. Results in coach_notes.md section 1. Not ported: lap splits straight from a connector stream with stops (`split_table` needs `run_series` from a FIT) |
| `sun.py` (10 Nov) | SUPERSEDED | own NOAA sunset for Brühl, written while the repo could not run; `cp.sun_times` gives about 1 min later and is the reference |
| inline: `cp.sun_times` cross-check (10 Nov) | HOUSEKEEPING | Thu 12 - Sun 20 Dec sunsets |
| inline: attachment inspection + diff of the attached coach_notes against the local copy (11 Nov) | HOUSEKEEPING | found CRLF line ends and blank lines holding a space |
| `normalize.py` (11 Nov) | PORTED | `cp_lib.normalize_md` (v1.7; selfcheck test) |
| inline: copy FITs, `fit_inspect`, `fit_laps`, `fit_pauses`, `aerobic_check`, `meter_offset` (11 Nov) | HOUSEKEEPING | library calls on tests/11_11_*.fit |
| `ride_11_11.py` (11 Nov) | ONE-OFF | per-second efforts on both meters, identical-sample check (Edge power = Stages), openers, HR around the max, 1-s HR jumps (Edge 8 vs MyWhoosh 33), RR count |
| `ride_11_11_b.py` (11 Nov) | ONE-OFF | trainer speed and FE-C resistance on the Edge around the efforts (found the dead KICKR in effort 2: the pulled power cable), wind-up before sprint 1, best windows, RR clock matching, `hrv_quality` |
| `ride_11_11_c.py` (11 Nov) | PORTED | power-based lag (0 s vs the HR lag of -4 s) and the masked cable-cut window → `meter_offset(align="power", mask=...)` (v1.6; selfcheck test); the rest ONE-OFF: sprint windows on both meters, 130 W block per 5 min, decoupling, Edge vs MyWhoosh HR |
| `rr_peak.py` (11 Nov) | PORTED | clean-beat peak HR (5-/10-beat means of beats within 12% of their 7-beat median) → `cp_lib.hr_peak_clean` (v1.7; selfcheck test: 194 / 192.9 / 192.5) |
| inline: `git pull` on the shallow clone (11 Nov) | HOUSEKEEPING | fails on a shallow clone with new commits ("divergent branches"): re-clone into a fresh folder instead |
| inline: cp_lib v1.6 edits + selfcheck runs (11 Nov) | HOUSEKEEPING | 39 passed after fixing an index error in the new test (band rows are lo, hi, n, other, ref, diff, ratio) |
| inline: history_digest.md and README / catalogue patches (11 Nov) | PATTERN | assert-once string replacement, the same idea as `cp.Patch` |
| inline: doc edits with the Edit tool on the local copies (11-12 Nov) | PATTERN | docs live in a local `docs/` copy, written back with `project_write(local_path=...)` |
| inline: clone of 12 Nov, comparison of repo files with the handover | HOUSEKEEPING | docs/coach_notes.md on GitHub was the 18:00 version (re-upload asked); the rest matched |
| inline: cp_lib v1.7 edits, `--index-md`, selfcheck (12 Nov) | HOUSEKEEPING | 41 passed |
| inline: Strava connector calls (all chats) | - | not commands; their results are in coach_notes.md |

- 11 Nov (cp_lib v1.6): `meter_offset(..., align="power", mask=...)`; `aerobic_check` and `hour_test_report` align by power by default (MyWhoosh HR about 4 s late on 11 Nov; power lag 0 s); docstring caveat on the band table next to ERG targets; selfcheck +2 tests on tests/11_11_garmin.fit + 11_11_kickr.fit (HR lag -4 / power lag 0 / KICKR +2% at 120-150 W; aerobic check 0: HR 149.6 / 160.9, ratios 0.979 / 0.991).
- 12 Nov (cp_lib v1.7): `normalize_md` (PATCH) and `hr_peak_clean` (FIT); selfcheck +2 tests (41 checks); README function index regenerated, `docs/` folder described.
- 12 Nov (cp_lib v1.8, segments_tool v1.4): rider weight 56 kg [Pat, measured; the 60 kg before was never weighed]: `CFG mass` 72 -> 68 kg (rider + bike 10.1 + kit about 2), `RIDER_KG` 60 -> 56; `segments_archive.csv` rebuilt (only the W/kg column changes; segments.md W/kg updated from it); all 41 checks still pass (physics outputs shift slightly: 20 min at 185 W 9.94 / 12.01 / 8.07 km, 1 Nov sprint meter/physics 1.07 / 1.09). README: data list as bullets per date, incl. tests/11_11_*.
- 12 Nov (cp_lib v1.9, analysis_tools v2.1): analysis_tools.py reviewed (unchanged since 1 Nov): `--ftp` / `--z2cap` now default to `cp_lib.CFG` (were fixed 175 / 135 W), `--lap` to 1265 m (U1 by GPS; was 1250); cp_lib `CFG ride_hr_zones` set to Pat's cycling zones of 8 Nov (132 / 148 / 162 / 177; unused so far, was the old 125 / 150 / 170 / 182); selfcheck +1 test (the CLI runs on tests/01_11.fit and reports the CFG FTP): 42 checks. (Later on 12 Nov, cp_lib v1.10: CFG ftp 180 -> 175 W from the hour test; `hour_test_report` docstring holds the result; selfcheck +1 test on tests/12_11_*.fit: 43 checks. Ad hoc: `hour_12_11.py` (per-minute power / HR / cadence, pacing phases, HR time in zones, CP sketches, targets from the FTP) = ONE-OFF.) (12 Nov evening, cp_lib v1.11: `wbal` (Skiba integral and differential W' balance), `wprime_needed` (smallest W' keeping W'bal >= 0), `pd_fit` (2P CP, CP fixed, Morton 3P) ported from the ad hoc `wprime.py` (power-duration bests from the 9 Nov digest CSV plus the 11/12 Nov Edge files, fits, W'bal on the hardest export rides); selfcheck +1 test on tests/01_11.fit: 44 checks.) Nothing else in analysis_tools.py was stale (it reads FIT, FIT.GZ and GPX, handles indoor files via `ensure_speed`, and its HR-flag counter stays documented as uninformative for rides).
- 14 Nov (no toolkit change): ad hoc `ride_14_11.py` (totals, best efforts on both meters, the final 3-min push per 30 s, W'bal at CP 175 / 18 kJ, steady-part decoupling, HR at 120-140 W) = ONE-OFF; `meter_14_11.py` (whole-ride and push-only alignment) and `erg_14_11.py` (the 15-min ERG hold at 120 W vs the Stages, aligned on the push) = PORTED in v1.12 below. Found: MyWhoosh drops frozen time when the app is in the background (file 4.0 min shorter, piecewise offsets), so a single whole-ride lag was wrong (lesson 19).
- 15 Nov (cp_lib v1.12): `meter_offset` gains `res["erg"]` (`erg_blocks`: every stretch where the other meter holds a constant ERG power for 2+ min, with both meters' averages on the same seconds; robust to the alignment), `res["seg"]` (`segment_lags`: lag per 10-min segment of the other file, reliable only where power varies), `res["warn"]` (piecewise offsets = reliable segment lags spread by more than 5 s; weak alignment r < 0.85 not confirmed by the segments) and `res["notes"]` (lengths differing by more than 60 s; weak r confirmed by segments). On the test files: 11 Nov ERG holds 129.5 / 149.6 W = ratio 1.022 / 1.011 (the same as the aerobic check), no warnings; 12 Nov r 0.70 confirmed by segments (note only); 14 Nov warns (segment lags -90 to 0 s; ERG holds at 120 W ratio 1.059 / 1.045 independent of the lag, push 0.998). selfcheck +2 tests (the 11/12 Nov files and a synthetic 2-min timer freeze cut into the 11 Nov KICKR file): 46 checks. README function index regenerated.
- 15 Nov evening (no toolkit change): ad hoc `ride_15_11.py`, `ride_15_11b.py`, `ride_15_11c.py` (5-min and 1-min all-outs: lap structure, meter_offset with the v1.12 warnings (piecewise offsets from app switches), per-effort alignment, per-15-s / per-10-s power, ERG check via the Edge resistance field and the KICKR's variability, best windows on both meters, HR recovery, easy-part HR, W'bal at CP 175 for 18-22 kJ, pd fits) = ONE-OFF (library calls plus printing).
- 17 Nov (cp_lib v1.13): new section RUN ZONES for the running threshold-HR and HR-zone review: `run_1hz` (1 Hz run series from GPX or FIT with stops, continuous-running clock and blanking of frozen HR), `run_hr_pace_windows` (steady 3-min windows), `run_hr_pace_model` (bpm per km/h with day offsets), `friel_run_pace_edges`, `friel_run_hr_zones`, `run_hr_zone_score` / `run_hr_zone_optimise` (HR zones vs pace zones; plateau of near-optimal edges), `vdot`, `vdot_pace`, `riegel_time`, `run_tt_report` (Friel LTHR estimate = HR of the last 20 min). Ported from the ad hoc `runwork/explore.py`, `runlib.py`, `a1.py`-`a3c.py` (7 export runs 3-28 Oct: 162 windows; model 6.7 bpm per km/h, HR at 5:00/km 173 on a mean day, day offsets -6 to +6, 12 Oct heat +10; 28 Oct 5K last 20 min 184.1; zone fit vs Strava pace zones 161 / 171 / 184, Z3/Z4 edge not pinned down). selfcheck +3 tests (VDOT / paces / Friel zones; run_tt_report on tests/28_10.fit; windows, model and zone fit on the export runs): 49 checks, about 1 min. README cookbook line and function index. Later on 17 Nov: Pat adopted the running HR zones with the Z5 edge raised to 188 [his definition: Z5 for efforts of about 5 min at most]; `CFG run_hr_zones` 130/160/175/190 -> 150/164/173/188 (exclusive bounds: Z1 <=149, Z2 150-163, Z3 164-172, Z4 173-187, Z5 >=188) and `CFG run_lthr` 181; the 5K zone-share test now expects 14 / 65 / 21% and still checks the old set (17 / 68 / 16%).
- 17 Nov evening (cp_lib v1.14): the check #1 files showed two weaknesses. (1) `aerobic_check` took the LONGEST stretch within +-10 W of each target: the 124.5 W Z2 block after the interval became "130 W" and the 160 W interval "150 W"; now the earliest stretch of at least 75% of the planned length with a mean within +-4 W (max_dev) is used, the longest only as a fallback, and with `other` the other file's HR is reported too (`other_hr_last`, the Edge's ANT+ HR). (2) `erg_blocks` used one ride-wide lag (+1 s) although a MyWhoosh timer freeze made the first hour about -72 s: the 10-min 150 W block read Stages 139.6 W instead of 146.5 W; new helper `_local_lag` aligns each block on its own transitions (local=True). Results 17 Nov: HR 135.1 / 146.4 at 130 / 150 W, KICKR/Stages 1.056 / 1.021 / 1.000 / 1.034 at 130 / 150 / 160 / 124.5 W. selfcheck +1 test on tests/17_11_*.fit (skipped until the files are in the repo): 50 checks. Ad hoc `fit_17_11/an.py` (laps, 5-min blocks, best windows, the interval per minute, the 30 s per 5 s, HR quality) = ONE-OFF.
- 18 Nov (no toolkit change): ad hoc `fit_18_11/an.py` (30-s all-out per 5 s and 1-s around it, best windows on both meters, the two 10-min intervals per 2 min with HR and decoupling, 5-min blocks, `erg_blocks` with local alignment, HR quality) = ONE-OFF; the v1.14 tools worked unchanged (local ERG-block lags -136 to -140 s while the ride-wide lag was off by timer freezes).

- 20 Nov (cp_lib v1.15, new digest_tool.py v1, selfcheck 65 checks): the digest overhaul. Prototype scripts in the sandbox (`ovlib.py`, `build_context.py`, `weather2.py`, `metrics.py`, `run_metrics.py`, `aug_tss.py`, `factors.py`, `hrmodel.py`, `hrmodel2.py`, `hrm.py`, `run_grid.py`, `fatigue_test.py`, `hci_ctx.py`, `hci.py`, `bests.py`) are PORTED: the general parts into the new cp_lib section METRICS (`session_1hz`, `stream_run_1hz`, `clean_hr`, `ride_load`, `run_load`, `hr_stats`, `aero_decoupling`, `efficiency_factor`, `hrr_events`, `pmc`, `lowpass` / `lowpass2`, `hr_intensity`, `hr_features`, `hr_model_fit`, `hr_model_sessions` (second, model-based HR cleaning pass), `hci_context`, `hci_zone_credit`, `hci_badness`, `hci_percentile`, `scale_score`, `value_percentile`, `lookup_rows`, `FTP_MONTH` / `ftp_for`), the pipeline and the markdown into `digest_tool.py`; the per-session inputs (strap ranges, MyWhoosh km, the 10 Nov stream, altitude, illness) moved from code into `data/session_context.csv`. The searches behind the choices are ONE-OFF (results in coach_notes.md section 4): HR-model grid (asymmetric lag 20 / 60 s + 15-min slow part, clip 1.3; runs gain only 3.76 vs 3.84 bpm from their own grid, so one set), fatigue measures by leave-one-out (TSB, ATL, previous day, 3 days, CTL), feel bootstrap and detection simulation, HRR rule review (two late-collapsing recoveries were strap artefacts: rule tightened). Weather: Open-Meteo's archive API hit its daily limit; the historical-forecast API worked (Brühl, Bibbona), Leutkirch from the export's weather columns.

- 21 Nov (no library change; digest_tool.py text edits): data corrections and recalibration. The 10 Nov run now comes from its Strava-made FIT (`tests/10_11.fit`, row src F, `hr_bad` 0-15.5) instead of the hand-copied stream; RPE 1 Nov 8, 15 Nov 5, 18 Nov 6 [Pat]; the 21 Nov outdoor ride added (`tests/21_11_garmin.fit`; weather provisional until the export). `digest_tool.py --calibrate` rerun (41 rides, reference 48 sessions; coefficients in coach_notes.md section 8). Ad hoc `r21.py` (stops, per-15-min power and HR, HR at power bands, strap artefacts, fuel per hour, route overlap with the routes zip) = ONE-OFF.
- 22 Nov (no library change; selfcheck 66 checks): 21 Nov RPE 5 [Pat] in `data/session_context.csv` (digest unchanged: HCI 76 either way; no recalibration, the 21 Nov coefficients stay). Five ridden segments added to `segments.json` with `fingerprint()` + `add_segment()` (Such dir ein schnelles Hinterrad!, Erp-Friesheim, L33 ost, Knallgas runter, Römersprint; all effort counts equal Strava's) and five to-do segments (No10 revers, Rampe nach Hemmerich, last 13%, Das Beste kommt meistens zum Schluss, Wand von Merten); `segments_archive.csv` rebuilt (122 found, 61 tracked). New selfcheck: the 21 Nov Erp-Friesheim / Knallgas runter efforts and the reversed Römersprint pass. Ad hoc in the sandbox (ONE-OFF): `c30/model.py` (route time at constant power with grade and wind, calibrated on the 21 Nov ride: factor 1.043), route overlap / shortcut / refill-distance checks for the 22 Nov route, segment-on-route direction check.
- 22 Nov evening (cp_lib v1.16, analysis_tools v3, routes_tool v3, segments_tool v1.5, new plans/make_plan.py, selfcheck 71 checks): the 22 Nov long ride and the 22 Nov export. PORTED: the hand analysis of the 21 / 22 Nov rides (`r21.py` and its inline follow-ups: stops, 15-min blocks, power bands, HR at power, first vs last hour, fuel per hour, daylight) -> `analysis_tools.long_ride_report` (`--report`); the route-time model (`c30/model.py`: physics per 20 m with grade and wind, 4 s per sharp turn, factor from the recorded rides) -> `routes_tool.route_time` / `calibrate_time` (TIME_FACTOR 1.046 from 1.043 and 1.049), with `analysis_tools.route_plan` (`--plan`); route overlap with the routes zip, straight-line cut options and refill places -> `routes_tool.route_overlap` / `shortcuts` / `near_places`; `routes_tool.parse` reads ride FITs; the segment-on-route direction check -> `segments_tool.on_route`; Pat's 22 Nov tracking wish (leave out efforts clearly below his ability, cap the listing) -> `segments_tool.capability` / `track_flags` (70% of the capability curve and 90% of FTP besides 80% of the PR) and the v1.5 `archive_md` (Strava's count instead of found / Strava, best tracked effort vs ability, a table of segments without a tracked effort); the numeric-token check of the 21 Nov coach-notes rewrite -> `cp_lib.doc_token_check`; the scratchpad plan generator -> `plans/make_plan.py` (relative paths, appends `plans/side_plan.md`). 22 new segments (13 attempted with references, all counts equal Strava's; 9 to-do) and No10 revers moved to attempted. ONE-OFF: forecasts from api.met.no (Open-Meteo stayed rate-limited), Google Maps place searches for Sunday refills, Strava segment pages for place names (login wall: name and town only), quäldich / climbfinder for the Bornheim climbs, PMC projections for week 3 (results in coach_notes.md section 7 and the plan notes); the C27 clock-time decision points (`route_time(...)['at_km']` at km 30 / 40 / 45 / 77 / 86.4 for three winds, `shortcuts` with custom windows: the km 45 -> 77 cut) and the plan-file fixes (week 2 Mon / Fri done, the week-4 run at 7 laps) in `plans/make_plan.py`; the docs review with `cp.doc_token_check` against the morning copies; the project instructions draft (version 22 Nov, handed to Pat, not in the repo); the handover check (selfcheck, digest, segments and plan rebuilt on a fresh copy of the 18 Nov commit) found that the `segments_tool.py` CLI rounded rel_cap to 0.1: it now keeps 3 decimals like the archive.

## Chat 3 archive (`archive/chat3_scripts.zip`, 22 Nov)
Pat asked on 22 Nov whether to hand over the chat-3 commands again (as the app export for chats 1-2). Claude built the archive from what the session still had: the script files that survived in the sandbox (10-22 Nov, `scripts/sandbox/`), the digest-v2 prototypes of 20 Nov (`scripts/overhaul_20_11/`) and every Bash command and file write since the last context reset (21 Nov 18:29 - 22 Nov 21:28, `commands/`, 253 files named `dd_mm.hh_mm[.n]` with `INDEX.tsv`: HOUSEKEEPING 114, PORTED 86, ONE-OFF 40, PATTERN 11, DOC 2). Inline commands of 10-21 Nov before that reset are no longer in the transcript; they were catalogued day by day above (11-21 Nov entries). An app export of chat 3 would only add the raw text of those inline commands, so it is optional.

| Script (archive path) | Category | Where it went / why |
|---|---|---|
| `sandbox/run_10_11.py`, `sun.py`, `normalize.py`, `ride_11_11*.py`, `rr_peak.py` | see the chat 3 (10-12 Nov) table | |
| `sandbox/eol_check.py` (12 Nov) | HOUSEKEEPING | CRLF / space-only-line check of attached docs -> `cp.normalize_md` |
| `sandbox/hour_12_11.py` (12 Nov) | PORTED | the hour-test breakdown -> `cp.hour_test_report` |
| `sandbox/wprime.py` (12 Nov) | PORTED | W' from the 4DP and the hour test -> `cp.wprime_needed`, `cp.wbal`, `cp.pd_fit` |
| `sandbox/ride_14_11.py`, `meter_14_11.py`, `erg_14_11.py`, `mo_test.py` (14-15 Nov) | ONE-OFF / PORTED | 14 Nov ride and meter comparison; ERG blocks -> `cp.erg_blocks` (v1.12); `mo_test.py` = a quick `meter_offset` trial |
| `sandbox/ride_15_11*.py` (15 Nov) | ONE-OFF | 5-min and 1-min all-outs (see the 15 Nov entry) |
| `overhaul_20_11/*.py` (20 Nov) | PORTED | digest v2 -> cp_lib v1.15 METRICS and `digest_tool.py` (see the 20 Nov entry) |
| `sandbox/ride_21_11.py` (21 Nov) | PORTED | -> `analysis_tools.long_ride_report` |
| `sandbox/mirror_restructure_21_11.py` (21 Nov) | ONE-OFF | the mirror regrouped into subcategories (line map, nesting, verified that no bullet was lost) |
| `sandbox/route_model_22_11.py` (22 Nov) | PORTED | -> `routes_tool.route_time` / `calibrate_time` |

## Chat 4 (from 22 Nov)
- 22 Nov, century v2 (C27 v2) check, ad hoc (not ported; the pieces are library calls): `routes_tool.analyse` / `compare_routes` / `route_overlap` (v2 vs v1 and the routes zip), `route_time` in five winds, `shortcuts` with custom early/late windows, `segments_tool.on_route`, `analysis_tools.py --plan` (11:00 / 11:30 starts). Fuel stations: Nominatim (OSM) `search?amenity=fuel&bounded=1&viewbox=...&extratags=1` (opening hours in `extratags.opening_hours`) plus `reverse?lat=&lon=` for komoot waypoint spurs, then `routes_tool.near_places` (max 700 m). Nominatim works from the sandbox with a User-Agent (about 1 request/s); the Overpass API does not.

- 26 Nov, 10-min all-out, KICKR vs Stages: an ad hoc script (`meter_compare.py`: fitparse records, a monotone lag path by dynamic programming over 90-s windows, band and window comparison), ported as `cp.align_monotone` / `cp.meter_compare` (cp_lib v1.17, selfcheck `meter_compare 26 Nov`); CP / W' refit and forecasts as `CFG['cp']` / `CFG['wprime']` / `CFG['wprime_icu']`, `cp.pd_predict`, `cp.pd_power_law` (selfcheck `pd_power_law / pd_predict`). Older pairs (11, 12, 17 Nov) rerun with the same method for the meter-ratio history.

## Gotchas learned along the way (all handled in the library)
- Weather from the sandbox (22 Nov): api.met.no's locationforecast (`https://api.met.no/weatherapi/locationforecast/2.0/complete?lat=..&lon=..`, needs a User-Agent header) works when Open-Meteo returns 429; hourly for about 2.5 days, then 6-hourly.
- The komoot connector's GPX link (mcp.main.komoot.net) downloads from the shell, but the track is simplified and trimmed near home (C30: 82.9 vs 85.2 km); Pat's own export is the geometry source.
- Garmin auto-pause and Strava segment times (22 Nov, Ortsschildsprint Brühl City): the file shows 2:20 with a 60 s pause, Strava 1:18; the tool keeps the elapsed time (elapsed-based power then flags it as weak), Strava sometimes leaves a paused minute out.
- `cp.hr_artefact_scan` can flag the minute after a long stop (HR still rising from about 110 while power is 150-200 W): a lag, not a strap fault (22 Nov min 95.4-99.5, 2% of the ride); judge by the HR a minute later.
- `np.convolve(..., mode='same')` pads the edges with zeros: fake climbs at every route start (fixed with edge padding).
- Strava-made run FIT files: the speed field is unreliable (smoothed phone speed); use the distance field. Garmin ride FITs have gaps where the timer was paused.
- A shallow clone (`--depth 1`) cannot `git pull` once new commits exist: clone again into a fresh folder.
- MyWhoosh's Bluetooth HR runs about 4 s behind the Edge's ANT+ HR (11 Nov): align two meters by power.
- The HR-flag counter in `analysis_tools.py` is capped at 8 and says nothing for 1 Hz ride files; use `hr_plateaus` / `hrv_quality` instead.
- `activities.csv`: timestamps are UTC; duplicated headers (`Elapsed Time.1`, `Distance.1`, ...); avg watts before the power meter (7-20 Aug) are Strava estimates.
- GPX run distance from raw GPS can over-read (14 Oct best 1K 3:51 vs Strava 4:01): trust Strava's best efforts for runs.
- Turn counts depend on the definition: window 100 m, 55°; C1 (4dp v2) has 28 unmerged, 17 with a merge radius of 350 m (the old v1 loop, no longer in the repo: 19 / 17).
- komoot exports come as tracks (`<trkpt>`) or routes (`<rtept>`, "komootGPXport"); both are read now.
- The sprint power check needs a lag-corrected window: the speed sensor trails power by 1-2 s.
- Shell quirks of the sandbox: `/bin/sh` has no `time` builtin and no process substitution; use `bash -c` or temp files.
- Stream data from the Strava connector cannot be piped into the sandbox: block-level analysis needs the FIT file; a short reduced-resolution stream can be copied into JSON by hand.
- MyWhoosh start_local can be off by tens of seconds (51 s on 6 Nov): align two recordings by cross-correlation, never by the stated start; by power where both have power (11 Nov: MyWhoosh HR 4 s late).
- Edge 540 indoors with GPS on: a GPS scribble, 0.13 km and 6 min "moving time" in Strava; Strava's moving time for that file is meaningless.
- Strava segment elevations (low/high) come from other devices and can be offset by 35-70 m; elevation differences agree with the Edge within about 3 m.
- HR lag: average HR of a short hard effort says little about strap quality; use the HR at its end.
- MyWhoosh FITs carry virtual GPS (a Belgian course) with sub_sport `virtual_activity`; the Edge indoors records `indoor_cycling`: outdoor tools (segments) must skip both.
- Strava segment power with an auto-paused stop inside the effort counts the stop as 0 W, i.e. it equals the elapsed-based value, not the average over recorded samples (31 Oct, 67 s stop: 147 vs 157 W).
- The Strava connector returns the run/default HR zone set, not the cycling set (app only).
- Strava draws missing HR as a flat ("frozen") line: look for gaps in the file, not for constant values.
- Open-Meteo: the archive API has a daily request limit for the sandbox's shared IP; the historical-forecast API (historical-forecast-api.open-meteo.com) gives the same hourly fields. Strava's export also carries weather columns (temperature, apparent temperature, humidity, wind in m/s) for many outdoor activities from mid-October.
- Python's `%.0f` rounds half to even: 174.5 W prints as 174 in one place and 175 in another when the float is 174.4999 / 174.5001; the digest tables come from one function, so they agree with each other.
- komoot GPX: a waypoint placed off the planned line becomes an out-and-back spur (a turn of about 170-180 degrees, 22 Nov C27 v2 km 24.2 and 78.7); scan the turn list for them. A re-export of an older tour can look like a new file (22 Nov: the zip's century.gpx = v1): compare geometry, not file names or bytes.
- MyWhoosh FIT timestamps are not wall-clock time (26 Nov): the start is stamped on a full minute (20:39:00 UTC for a ride the Edge started at 20:35:17) and frozen seconds are simply missing, so the file is 227 s shorter; its best 10 min sat 194 s 'later' than the Edge's. Never align by timestamps: use `cp.meter_compare` (lag path in record order).
- A meter ratio taken from a test alone can mislead: compare by power band against earlier dual sessions (the KICKR / Stages ratio falls with power on every day: about 1.03 in Z2, 1.00 at 150-175 W, 0.99 at 200-250 W from 11-17 Nov), and look for a level shift (26 Nov: 3-5% lower at all powers, after outdoor riding and the bike swap).

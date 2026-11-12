# Script catalogue

Where the commands of chats 1-2 went. Source: Pat's archive `all_accessible_commands_with_outputs.zip` (87 files, commands up to 1 Nov 13:18; one duplicate removed, hours zero-padded). The archive is not needed in the repo any more: this file records every disposition.

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
| `03_10.19_41.3` | PORTED | aero model (brentq power → speed) → `cp_lib.speed_from_power` (71 kg / CdA 0.40 then; now 72 kg / 0.38 via CFG) |
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
- 11 Nov (cp_lib v1.6): `meter_offset(..., align="power", mask=...)`; `aerobic_check` and `hour_test_report` align by power by default (MyWhoosh HR about 4 s late on 11 Nov; power lag 0 s); docstring caveat on the band table next to ERG targets; selfcheck +2 tests on tests/11_11_garmin.fit + 11_11_kickr.fit (HR lag -4 / power lag 0 / KICKR +2% at 120-150 W; aerobic check 0: HR 149.6 / 160.9, ratios 0.979 / 0.991). Ad hoc in chat 3: sprint windows on both meters, the cable-cut window, a clean-beat RR peak (5-/10-beat means of artefact-free beats) for the 194 bpm max.
- Progress checks for the 6-week plan → `cp_lib.aerobic_check` (cp_lib v1.5): finds the 130 W / 150 W blocks of the aerobic check in a ride file, HR of the last 10 / 5 min, drift, W/HR, optional second recording for the meter ratio; selfcheck test on synthetic data plus the hilly 7 Nov file (no block). The other checks use existing tools (`ride_session` decoupling, `run_series` / `split_table`).
- `selfcheck.py`: the old 4DP v1 route test (its GPX is no longer in the repo, so it was always skipped) is replaced by the same merge-rule and smoothing check on C1 (4dp v2: 28 / 17 turns, +166/-168 m); the support branch for the old C19 file (approach + loop), the old `rides_runs_gpx_files_*.zip` pattern and old test-file names (`5k_28oct.fit`, `4dp_01_11.fit`) are removed. 37 checks, none skipped with the current zips.

## Gotchas learned along the way (all handled in the library)
- `np.convolve(..., mode='same')` pads the edges with zeros: fake climbs at every route start (fixed with edge padding).
- Strava-made run FIT files: the speed field is unreliable (smoothed phone speed); use the distance field. Garmin ride FITs have gaps where the timer was paused.
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

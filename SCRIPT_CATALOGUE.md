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

## Gotchas learned along the way (all handled in the library)
- `np.convolve(..., mode='same')` pads the edges with zeros: fake climbs at every route start (fixed with edge padding).
- Strava-made run FIT files: the speed field is unreliable (smoothed phone speed); use the distance field. Garmin ride FITs have gaps where the timer was paused.
- The HR-flag counter in `analysis_tools.py` is capped at 8 and says nothing for 1 Hz ride files; use `hr_plateaus` / `hrv_quality` instead.
- `activities.csv`: timestamps are UTC; duplicated headers (`Elapsed Time.1`, `Distance.1`, ...); avg watts before the power meter (7-20 Aug) are Strava estimates.
- GPX run distance from raw GPS can over-read (14 Oct best 1K 3:51 vs Strava 4:01): trust Strava's best efforts for runs.
- Turn counts depend on the definition: window 100 m, 55°, merge radius 350 m (17 on the old 4DP loop) vs unmerged (19).
- komoot exports come as tracks (`<trkpt>`) or routes (`<rtept>`, "komootGPXport"); both are read now.
- The sprint power check needs a lag-corrected window: the speed sensor trails power by 1-2 s.
- Shell quirks of the sandbox: `/bin/sh` has no `time` builtin and no process substitution; use `bash -c` or temp files.
- Stream data from the Strava connector cannot be piped into the sandbox: block-level analysis needs the FIT file.

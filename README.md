# cycling_running: coaching toolkit

This README is the index of the toolkit. It is synced into the Project and read in every chat; the code itself is only opened when it is used.

The repo is public and the sandbox can clone it. Claude cannot push to GitHub: new or changed files are handed over in the chat and Pat commits them.

## Start of a chat that needs analysis (the sandbox resets every chat, sometimes mid-chat)
```sh
git clone --depth 1 https://github.com/unterrunden/cycling_running repo && cd repo
pip install fitparse scipy pandas --break-system-packages -q
python3 selfcheck.py        # 37 checks (under 1 min): every PASS = the toolkit still reproduces the validated numbers
```

Data in the repo: the newest `strava_export_<dd_mm>.zip` (full Strava export: `activities.csv`, the activity files and `routes/`) and `all_routes_<dd_mm>.zip` (route GPX files). Segments: `segments.json` (definitions + reference lines) and `segments_archive.csv` (every effort, rebuilt by `segments_tool.py`). Optional test files: `tests/28_10.fit` (28 Oct 5K), `tests/01_11.fit` (1 Nov 4DP), `tests/06_11_stages_series.json` + `tests/06_11_kickr_streams.json` (6 Nov KICKR vs Stages, no GPS), `tests/07_11_garmin.fit` + `tests/07_11_kickr.fit` (7 Nov, both recordings at 1 Hz; Edge indoors without GPS, MyWhoosh virtual coordinates), `tests/09_11_digest_rides.csv` + `tests/09_11_digest_runs.csv` (digest CSVs of the 9 Nov export, for the digest-generator test).

Newer activities: the Strava connector gives summaries; FIT / GPX files uploaded in the chat or a newer export in the repo give block-level detail. Connector streams cannot be piped into the sandbox; a reduced-resolution stream (resolution <= ~300) can be copied into a JSON file by hand (`cp.stream_series`).

## Files
| File | Purpose |
|---|---|
| `analysis_tools.py` | v2 CLI: one GPX / FIT / FIT.GZ activity → ride report (elapsed-based and stops-excluded power curves up to 180 min, NP, zones, cadence, HR) or run report (splits, laps, HR at pace); `--batch` → digest CSVs |
| `routes_tool.py` | v2: GPX route geometry from komoot track exports (`<trkpt>`) and route exports (`<rtept>`): distance, ascent, sharp turns (with merge option), stretches and headings, moderate bends, loop closure, comparison, markdown entries |
| `cp_lib.py` | Everything else: physics (power / speed / wind, CP sketches), sun times, FIT inspection (laps, pauses, HRV / strap quality), ride blocks and windows, run trial tools, 4DP report, CSV and digest generator, safe markdown patcher |
| `segments_tool.py` | v1.3: Strava segments without a segment API: fingerprint a PR effort in the ride files, reference lines, every effort of every segment (time, W, cadence, HR, stops) → `segments_archive.csv` (tracked efforts only: elapsed-based power >= 80% of the PR power) and the tables of the `claude/segments.md` Project doc; HR artefact check, rides with unusable HR; indoor FITs (MyWhoosh virtual GPS, Edge indoor profile) are skipped |
| `segments.json` | Segment definitions (Pat's Strava values, status attempted / todo), 25-point reference lines, thresholds (`tracking`, `hr_check`) and `hr_unusable` rides |
| `selfcheck.py` | Regression test (see above); picks the newest data zips automatically |
| `SCRIPT_CATALOGUE.md` | Where the commands of the chats went (ported / superseded / one-off) and the gotchas learned on the way |

## Cookbook (task → command; `import cp_lib as cp, routes_tool as rt`)
- First look at any FIT: `cp.fit_inspect(f)`. Lap-button blocks, pauses, strap: `cp.fit_laps(f)`, `cp.fit_pauses(f)`, `cp.fit_events(f)`, `cp.hrv_quality(f)`.
- Ride report: `python3 analysis_tools.py f.fit --ftp 175`; session view (blocks, best windows with HR and speed, decoupling, efforts): `cp.ride_session(f)`.
- 4DP / Full Frontal: `cp.fourdp_report(f)` (sprints with a physics check, per-minute blocks, gaps with stopped time, strap quality, FTP by the 4DP rule).
- Window / block detail: `a, ex, tl = cp.load_activity(f)`; `cp.best_window(tl, 1200, 'elapsed')`; `cp.ride_blocks(tl, 10)`.
- Run trial: `cp.run_finish_report(f)`; reps: `rs = cp.run_series(f)`; `cp.fastest_windows(rs, 240, 3)`; `cp.split_table(rs, 500)`.
- Routes: `python3 routes_tool.py DIR`; `--compare A B`; `--diag F`; `--entry F C28`; in Python `rt.analyse(f, merge_km=0.35)`, `rt.stretches(r)`, `rt.moderate_bends(f)`, `rt.loop_closure(f)`.
- Wind and distance: `cp.distance_table(powers=(180, 185, 190), winds=(-10, 0, 10))`; `cp.implied_headwind(174, 27.2, 0.0056)`; `cp.cp_fit([(300, 231), (1200, 184)])`.
- Daylight: `cp.sun_times(datetime.date(2026, 11, 29))`.
- Digest refresh: `python3 analysis_tools.py --batch EXPORT/activities --csv EXPORT/activities.csv --out digest --ftp 180` (the batch dir is the export's `activities` folder), then `cp.make_history_digest('digest/digest_rides.csv', 'digest/digest_runs.csv', 'history_digest.md', strava_now=cp.parse_bests('5s=686@2026-11-01, ...'), strava_virtual=cp.parse_bests('5s=413@2026-11-06, ...'), ftp=180, asof='...', export_name='Strava export of ...', hr_notes={'2026-10-17': '(HR unusable, Pat)'}, run_notes='...', after_archive_md=[...])`. Ride and VirtualRide bests come from the connector (`get_athlete_best_efforts`); outdoor and indoor rides are kept apart; a Strava best newer than the export shows in bold, and `extra_monthly` adds it to the monthly table. New bests go into the tables, not into extra text.
- Segments: `python3 segments_tool.py` (newest export + tests/*.fit → `segments_archive.csv` + markdown); new segment: `acts = st.load_rides(); st.fingerprint(acts, km=1.56, time_s=221, w=248, cad=88, hr=183, hrmax=189)`, then `st.add_segment(...)`, `st.save_segments(data)` (`import segments_tool as st`).
- 60-min FTP test (or any long test): `cp.hour_test_report(edge_fit, other=kickr_fit)` (best window, 5-min blocks, halves, decoupling, LTHR estimate = HR of the last 20 min, KICKR vs Stages on the same window).
- HR quality and zones: `cp.hr_artefact_scan(tl)` (minute ranges where HR cannot match the power: 200 W / 45 s and 150 W / 2 min tiers), `cp.hr_gaps(tl)` (missing HR while riding; Strava draws it as a frozen line); `w = cp.hr_power_windows(tl)` per ride, stacked → `cp.hr_zone_score(w, [133, 148, 162, 173], ftp)` / `cp.hr_zone_optimise(w, ftp)`.
- Progress checks (coach_notes.md section 7): aerobic check `cp.aerobic_check(kickr_fit, other=edge_fit)` (20 min at 130 W + 10 min at 150 W: HR of the last 10 / 5 min, drift, W/HR, meter ratio); long-ride durability `cp.ride_session(f)` (decoupling); run pace and HR per lap `cp.split_table(cp.run_series(f), 1265)`.
- Two power meters at once (KICKR vs Stages): `cp.meter_offset(cp.fit_series(edge_fit), cp.fit_series(kickr_fit))` (aligns by HR, power-band table, linear fit); a stream instead of a FIT: `cp.stream_series(streams, '2026-11-06T15:51:40')`.
- Edit markdown safely: `p = cp.Patch('coach_notes.md'); p.rep(old, new, 'tag'); p.insert_after('- [stated] ...', new); p.save('out.md')` (refuses to save if any target is missing).

## Conventions
- Elapsed-based = Strava power-curve convention (stopped or paused seconds count as 0 W); rolling / moving = stopped seconds removed, coasting kept (Strava average-power convention).
- FTP settings in Strava and intervals.icu: 170 W (since 1 Nov); 4DP result 183-184 W; the planning FTP is set after the 60-min trainer test. 4DP Full Frontal: FTP = 100% of the 20-min average. Model and zone defaults live in `cp_lib.CFG`.
- Local time Europe/Berlin; `activities.csv` timestamps are UTC.
- Power scales: outdoor = Stages (left-only), indoor = KICKR. So far the KICKR reads about +5 W at Z2 power, about the same at threshold power and normal cadence (7 Nov: +4% overall), about +8% below 60 rpm (6 Nov: +8-10 W). Keep the two apart; settle the offset with `cp.meter_offset` on dual recordings.

## Gotchas (details in `SCRIPT_CATALOGUE.md`)
- Strava-made run FIT files: use the distance field, not speed. Garmin ride FITs have gaps where the timer paused. GPX run distance can over-read; trust Strava's best efforts for runs.
- The HR-flag counter in `analysis_tools.py` is capped at 8 and uninformative for rides: use `cp.hr_plateaus` / `cp.hrv_quality`.
- Turn counts depend on the definition: 100 m windows, 55°; C1 (4dp v2) has 28 unmerged, 17 with a merge radius of 350 m.
- komoot GPX has no surface, crossing or traffic-light data; komoot elevation is noisy (ascent ±10%, occasional spikes: see `rt.elevation_diag`).
- Trainer rides are a separate Strava sport (VirtualRide) with their own best efforts; trainer HR without a strong fan is inflated.
- HR lags 30-90 s: genuine 45-s efforts at 200+ W can average 128-142 bpm; judge strap artefacts by the HR at the end of an effort (or falling HR), not by the average.
- The Strava connector returns the run/default HR zones (<130/160/175/190), not the cycling set kept in the app.
- MyWhoosh start times can be off (51 s on 6 Nov): align by HR (`cp.meter_offset`). Edge 540 HRV messages hold some junk RR values (6-58 s), now ignored. An Edge recording indoors with GPS on draws a scribble and uploads a 0.1 km outdoor "Ride" to Strava: use an indoor profile and delete the duplicate.
- MyWhoosh FITs carry virtual GPS (sub_sport `virtual_activity`), the Edge indoors records `indoor_cycling`: outdoor tools (segments) skip both.
- Strava segment power with an auto-paused stop inside the effort counts the stop as 0 W (= the elapsed-based value; 31 Oct, 67 s stop: 147 vs 157 W over recorded samples).
- A best-effort curve can rise with duration (4 Nov: 10 min 177 W > 8 min 176 W): harder stretches at both ends of the window, not an error.
- The sandbox shell is `sh`: no `time` builtin, no process substitution (use `bash -c` or temp files).

## When the toolkit changes
Claude hands over the changed files, Pat commits them, then `python3 selfcheck.py` runs. Every new function gets a test against a validated number. Keep this README short: it is read in every chat.

## `cp_lib.py` function index (generated by `python3 cp_lib.py --index-md`)


### CONFIG
- `fmt_t`: Seconds -> m:ss text (e.g. 1410 -> 23:30).

### PHYSICS
- `power_needed`: Pedal power (W) needed for ground speed v_kmh on a grade (fraction); wind_kmh > 0 = headwind.
- `speed_from_power`: Ground speed (km/h) for pedal power P (W).
- `implied_headwind`: Headwind (km/h, negative = tailwind) that the model needs to explain speed v_kmh at power P.
- `effort_distance`: Distance (km) covered in `minutes` at constant power P: how long a corner-free stretch must be.
- `distance_table`: Table of effort distance by power (rows) and wind (columns, + = headwind km/h).
- `cp_fit`: Two-parameter critical-power sketch from [(seconds, watts), ...] (>= 2 points; least squares of work vs time).
- `cp_predict`: Power (W) the critical-power sketch predicts for an effort of `seconds` (CP + W'/t).

### SUN
- `sun_times`: (sunrise, sunset) as 'HH:MM' local time for date d (NOAA approximation, DST-aware).

### PATCH
- `Patch`: Safe edits of a text file.

### FIT
- `fit_inspect`: First look at a FIT file: producer/device, sport, session summary, record channels and counts, time span, gaps, timer events, laps, HRV.
- `fit_laps`: Lap table (lap button / auto laps): start (local), elapsed, timer, distance, power, HR, cadence, ascent, work, trigger.
- `fit_events`: Timer events (start / stop_all with trigger auto|manual), markers, off-course notices.
- `fit_pauses`: Timer pauses: from each stop_all to the next start: offset into the file, duration, and what triggered the stop (auto / manual).
- `hrv_quality`: Beat-to-beat (RR) quality from the FIT 'hrv' messages (Garmin ride files; Strava-made files have none).

### LOADING (uses `analysis_tools.py`)
- `load_activity`: Load a GPX / FIT / FIT.GZ activity.

### RIDE
- `ride_blocks`: Table of consecutive blocks of MOVING time (stops removed): avg W, NP, HR avg/max, pedalling cadence.
- `best_window`: Best mean-power window of dur_s seconds.
- `decoupling`: Aerobic decoupling over a power / HR series (same length, e.g. moving seconds): efficiency factor (NP/HR) of the 1st vs 2nd half.
- `hr_by_power`: Mean HR and seconds per power band (default bands: <100, 100-135, 136-155, 156-180, >180 W).
- `find_efforts`: Find hard efforts in a power series (1 Hz): start when 5-s mean >= start_w (default 1.2 x FTP), continue while >= hold_w (default 0.97 x FTP), keep those >= min_len s.
- `ride_session`: One-call post-ride summary of a ride file: totals, 10-min blocks, best windows (elapsed + moving) with HR/speed, decoupling, HR by power, efforts.

### RUN
- `run_series`: Distance-based series of a run: dict with t (s), dist (m, recorded distance if the file has it), mt (moving-time axis, pauses removed), hr, lat, lon.
- `split_table`: Splits every `step` metres (moving time): from_m, to_m, time_s, pace_s_km, hr_avg, hr_max.
- `halves`: First vs second part of a run (default: half distance): times, paces and how much faster the second part was (%, positive = negative split).
- `tail_paces`: Time and pace over the last L metres of a run, for each L.
- `fastest_windows`: Fastest non-overlapping windows of window_s seconds (for interval runs / reps): start (moving min), pace, distance, HR avg/max.
- `hr_plateaus`: Runs of >= min_len identical consecutive HR readings (possible held values / strap trouble) and the count of NaN seconds.
- `hr_steps`: Sudden HR steps (mean of the next `win` s vs the previous `win` s differs by >= thr bpm, at most one per minute).
- `hr_zone_time`: Share of valid HR seconds per zone.
- `loop_length`: Length (m) of the first lap of a loop course: first return within `tol` m of the start after min_m metres (None if none).
- `run_finish_report`: One-call summary for a trial / race run: km splits with HR, 500 m splits, halves, tail paces, HR zone shares, HR plateaus, loop length.

### TESTS
- `top_windows`: Best `n` non-overlapping mean-power windows of `dur_s` seconds in p[lo:hi] (at least `sep_s` apart).
- `sprint_energy_check`: Plausibility check of a sprint's power (seconds s..e of the timeline): meter energy vs the physics needed for the measured acceleration plus drag.
- `fit_series`: FIT -> dict(t=epoch seconds, p, hr, cad) of the record messages, for meter_offset().
- `stream_series`: Strava connector streams (dict with time, watts, heart_rate; any resolution) + the activity's start_local ('2026-11-06T15:51:40') -> dict(t=epoch seconds, p, hr).
- `meter_offset`: Compare two power meters recorded at the same time (e.g. ref = Edge/Stages FIT, other = KICKR via MyWhoosh FIT or stream).
- `hr_artefact_scan`: Minute ranges where HR cannot match the power (strap artefacts).
- `hr_gaps`: Stretches of riding (power or speed present) with missing or zero HR (strap lost) of at least min_s seconds (short gaps inside a stretch end it): [(from_min, to_min)].
- `hr_power_windows`: Quasi-steady windows of one ride for HR-zone work: every 60 s a `win_s` window (after the first `skip_s`), moving throughout, 10-s power CV <= max_cv; HR = mean of its last `hr_last_s` s (HR lag).
- `hr_zone_score`: How well 5 HR zones (upper edges, e.g. [133, 148, 162, 173]: Z1 < 133 ...) reproduce the power zone (Coggan 5-zone fractions of ftp) of each window.
- `hr_zone_optimise`: Grid search of the Z2/Z3, Z3/Z4 and Z4/Z5 HR edges (Z1 edge fixed: few steady recovery windows) maximising hr_zone_score's balanced accuracy.
- `hour_test_report`: Analyse a long all-out test (default the 60-min FTP test) from one FIT (e.g. Edge/Stages), optionally a second recording of the same ride (`other`, e.g. the MyWhoosh/KICKR FIT): best `dur` window (elapsed: pauses count as 0 W), per-block W / HR / cadence, halves, pacing CV of 1-min means, Pw:HR decoupling, HR drift, LTHR estimate = average HR of the last `lthr_last_s` seconds (Friel), NP; with `other`: its average over the same (HR-aligned) window and the meter_offset table.
- `aerobic_check`: Aerobic check (progress check for goal a, every second week): 20 min at 130 W, then 10 min at 150 W, inside the Z2 part of a ride (KICKR, fan, usual room).
- `fourdp_report`: Analyse a 4DP / Full Frontal file (two 5-s sprints, 5 min, 20 min, 1 min, in that order) without laps or manual input.

### CSV / DIGEST
- `load_activities_csv`: Strava export activities.csv -> clean DataFrame (pandas renames the duplicate headers 'Elapsed Time.1', 'Distance.1', 'Max Heart Rate.1', 'Relative Effort.1'; the .1 versions are the numeric ones in seconds / metres).
- `csv_totals`: Counts, km and hours by activity type, and km by gear (use to cross-check against Strava: connector gear totals, profile counts).
- `parse_bests`: Parse current Strava all-time bests typed in by hand, e.g. "5s=686@2026-11-01, 20min=184@2026-11-01", into {'5s': (686.0, '2026-11-01'), ...}.
- `bests_table_md`: Markdown rows of the all-time bests table from the rides digest DataFrame (columns `el_<dur>`, `ro_<dur>`, date).
- `monthly_bests_md`: Bests by month (elapsed-based) for 5s, 1min, 5min, 10min, 20min and 60min.
- `weekly_table_md`: Weekly load/intensity rows from the rides digest: rides (V = virtual/indoor), km, moving h, TSS-like, Z1-2 / Z3 / Z4+ shares (Z1-2 < 75%, Z3 75-90%, Z4+ >= 90% of the FTP used in the batch).
- `make_history_digest`: Write history_digest.md from digest_rides.csv / digest_runs.csv (made by `analysis_tools.py --batch --ftp <ftp>`).

### INDEX
- `index`: Print the function index of this module grouped by section (md=True: markdown for README.md).

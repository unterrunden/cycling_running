# History digest: Pat, cycling | running

As of: Strava export of 9 Nov 2026 (strava_export_09_11.zip, 59 activities); activities to 08 Nov; tables updated 9 Nov 2026 (Strava bests as of 9 Nov); section 8 and the 'Strava VirtualRide now' column updated 12 Nov 2026.

Source: Strava export of 9 Nov 2026 (strava_export_09_11.zip, 59 activities) analysed with analysis_tools.py v2 and cp_lib.make_history_digest. Outdoor rides: 46 (33 with power, from 29 Aug; without power: 07 Aug-20 Aug, 26 Sep). Virtual rides (MyWhoosh, KICKR power): 6. Runs: 7. FTP for zones: 180 W (working value, Stages scale).

## 1. Method and validation

- **elapsed-based** = Strava power-curve convention (paused/stopped seconds count as 0 W). **rolling** = only recorded seconds with speed >= 1.0 m/s, coasting (0 W) kept; this matches Strava's 'average power' convention (stops excluded, coasting included).
- Validation: the elapsed-based bests of the outdoor rides reproduce Strava's all-time Ride power curve (table 2), and the rolling 60-min value on 22 Sep (170.0 W) equals the 170 W average of that 59:54 ride. NP/avg of the 20 Sep ride also match (avg 149 W, NP 156 W).
- Two power meters: outdoor rides use the Stages (left-only), virtual rides the KICKR (about +5 W at Z2 power, about equal at threshold power and normal cadence, about +8% below 60 rpm). Outdoor and indoor bests are therefore kept apart (Strava does the same: Ride vs VirtualRide).
- HR: judge max HR by the 30-s mean (column in brackets); rides with unusable HR stretches are marked in table 5 (see section 7).

## 2. All-time bests, outdoor rides (Stages, W)

| Duration | Elapsed-based (archive) | Date | Strava all-time now | Date | Rolling (stops excl., archive) | Date |
|---|---|---|---|---|---|---|
| 5s | 686 | 01 Nov | 686 | 01 Nov | 686 | 01 Nov |
| 15s | 448 | 30 Oct | 448 | 30 Oct | 448 | 30 Oct |
| 30s | 397 | 17 Oct | 397 | 17 Oct | 397 | 17 Oct |
| 1min | 317 | 27 Sep | 316 | 27 Sep | 317 | 27 Sep |
| 2min | 279 | 27 Sep | 279 | 27 Sep | 279 | 27 Sep |
| 3min | 258 | 17 Oct | 258 | 17 Oct | 258 | 17 Oct |
| 5min | 231 | 01 Nov | 231 | 01 Nov | 231 | 01 Nov |
| 8min | 203 | 02 Oct | 203 | 02 Oct | 203 | 02 Oct |
| 10min | 202 | 02 Oct | 202 | 02 Oct | 202 | 02 Oct |
| 15min | 187 | 02 Oct | 187 | 02 Oct | 188 | 16 Sep |
| 20min | 184 | 01 Nov | 184 | 01 Nov | 184 | 01 Nov |
| 30min | 171 | 01 Nov | 171 | 01 Nov | 184 | 16 Sep |
| 45min | 164 | 02 Oct | 163 | 02 Oct | 176 | 22 Sep |
| 60min | 157 | 19 Sep | 157 | 19 Sep | 170 | 22 Sep |
| 90min | 147 | 19 Sep | n/a | - | 156 | 19 Sep |
| 120min | 144 | 20 Sep | n/a | - | 151 | 19 Sep |
| 150min | 141 | 20 Sep | n/a | - | 150 | 20 Sep |

Notes: the 180-min elapsed value is a stop-heavy artefact and not reported. The rolling 20/30-min values of 16 Sep include short stops inside the window, so they overstate a continuous effort slightly. No Strava best is newer than this export.

### Indoor bests (virtual rides, KICKR, W)

| Duration | Elapsed-based | Date | Strava VirtualRide now |
|---|---|---|---|
| 5s | 413 | 06 Nov | 587 (11 Nov) |
| 15s | 365 | 06 Nov | 534 (11 Nov) |
| 30s | 299 | 08 Nov | 433 (11 Nov) |
| 1min | 272 | 06 Nov | 293 (11 Nov) |
| 2min | 209 | 03 Nov | 209 (03 Nov) |
| 3min | 199 | 07 Nov | 199 (07 Nov) |
| 5min | 182 | 04 Nov | 182 (04 Nov) |
| 8min | 176 | 04 Nov | 176 (04 Nov) |
| 10min | 177 | 04 Nov | 177 (04 Nov) |
| 15min | 172 | 04 Nov | 172 (04 Nov) |
| 20min | 138 | 07 Nov | 178 (12 Nov) |
| 30min | 136 | 07 Nov | 177 (12 Nov) |
| 45min | 132 | 07 Nov | 176 (12 Nov) |
| 60min | 133 | 07 Nov | 175 (12 Nov) |

Indoor sessions so far without a strong fan (HR inflated). Where a longer duration shows a higher value than a shorter one (04 Nov: 10min 177 W > 8min 176 W; 07 Nov: 60min 133 W > 45min 132 W), it is genuine, not an error: a window with harder stretches at both ends can average more than any shorter window inside it.

## 3. Bests by month, outdoor rides (elapsed-based, W)

| Month | 5s | 1min | 5min | 10min | 20min | 60min |
|---|---|---|---|---|---|---|
| 2026-08 | 473 | 273 | 210 | 182 | 154 | 137 |
| 2026-09 | 510 | 317 | 213 | 201 | 175 | 157 |
| 2026-10 | 544 | 290 | 203 | 202 | 174 | 155 |
| 2026-11 | 686 | 312 | 231 | 187 | 184 | 138 |

## 4. Weekly load and intensity (all rides with power, FTP 180 W)

Z1-2 = below 75% FTP (< 135 W), Z3 = 75-90% (135-162 W), Z4+ = 90% FTP and above (>= 162 W). TSS-like = duration x IF^2 x 100 from NP. Indoor sessions (V) are KICKR power.

| Week of | Rides (V = indoor) | km | Moving h | TSS-like | Z1-2 % | Z3 % | Z4+ % |
|---|---|---|---|---|---|---|---|
| 2026-08-24 | 3 | 34 | 1.4 | 127 | 55 | 8 | 37 |
| 2026-08-31 | 6 | 216 | 8.5 | 641 | 40 | 25 | 35 |
| 2026-09-07 | 5 | 189 | 7.4 | 658 | 35 | 24 | 41 |
| 2026-09-14 | 5 | 219 | 8.4 | 719 | 28 | 33 | 39 |
| 2026-09-21 | 5 | 200 | 7.9 | 642 | 38 | 26 | 36 |
| 2026-09-28 | 3 | 93 | 3.4 | 296 | 30 | 30 | 40 |
| 2026-10-05 | 1 | 35 | 1.4 | 110 | 33 | 41 | 26 |
| 2026-10-12 | 2 | 51 | 2.0 | 138 | 60 | 25 | 15 |
| 2026-10-26 | 3 | 159 | 6.4 | 433 | 58 | 19 | 23 |
| 2026-11-02 | 6 (6 V) | 99 | 3.6 | 233 | 74 | 12 | 14 |

All power rides: Z1-2 42%, Z3 25%, Z4+ 33% of pedalled time; 43% of time at or below the 135 W easy cap. Reading (my view): most riding so far was tempo and above; the plan's base work needs a deliberately larger Z1-2 share.

## 5. Per ride (rides with power; V = indoor, KICKR)

| Date | | km | Moving min | Avg W (moving) | NP | IF | % time <=135 W | HR avg/max (30 s max) | Cadence |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-29 |  | 0.6 | 2 | 121 | 154 | 0.86 | 65 | - | 59 |
| 2026-08-29 |  | 11.7 | 26 | 158 | 185 | 1.03 | 32 | - | 80 |
| 2026-08-30 |  | 21.8 | 55 | 118 | 167 | 0.93 | 66 | - | 72 |
| 2026-08-31 |  | 40.3 | 97 | 134 | 151 | 0.84 | 36 | - | 75 |
| 2026-09-01 |  | 11.1 | 28 | 121 | 160 | 0.89 | 60 | 144/182 (178) | 71 |
| 2026-09-02 |  | 35.7 | 84 | 137 | 167 | 0.93 | 47 | 154/187 (185) | 78 |
| 2026-09-03 |  | 33.7 | 79 | 144 | 164 | 0.91 | 40 | 155/181 (180) | 73 |
| 2026-09-05 |  | 40.0 | 91 | 146 | 159 | 0.88 | 32 | 148/175 (173) (HR? min 20-36) | 74 |
| 2026-09-06 |  | 55.5 | 130 | 132 | 146 | 0.81 | 42 | 146/174 (172) | 76 |
| 2026-09-08 |  | 28.1 | 64 | 149 | 163 | 0.90 | 24 | 159/187 (186) | 75 |
| 2026-09-09 |  | 33.4 | 79 | 147 | 178 | 0.99 | 45 | 149/183 (182) | 74 |
| 2026-09-10 |  | 32.1 | 77 | 151 | 180 | 1.00 | 38 | 132/181 (178) (HR gaps/dropouts min 13-58) | 77 |
| 2026-09-12 |  | 51.5 | 123 | 140 | 165 | 0.92 | 42 | 150/187 (184) | 75 |
| 2026-09-13 |  | 43.6 | 100 | 150 | 164 | 0.91 | 26 | 147/176 (176) | 76 |
| 2026-09-15 |  | 27.5 | 62 | 149 | 160 | 0.89 | 26 | 156/181 (180) | 77 |
| 2026-09-16 |  | 33.5 | 79 | 153 | 181 | 1.01 | 38 | 149/185 (184) | 77 |
| 2026-09-17 |  | 34.2 | 77 | 156 | 183 | 1.02 | 41 | 150/184 (181) | 78 |
| 2026-09-19 |  | 53.7 | 122 | 151 | 164 | 0.91 | 29 | 157/184 (182) | 76 |
| 2026-09-20 |  | 70.2 | 161 | 149 | 156 | 0.87 | 19 | 147/175 (172) | 79 |
| 2026-09-22 |  | 28.4 | 60 | 170 | 178 | 0.99 | 12 | 163/186 (184) | 82 |
| 2026-09-23 |  | 42.2 | 95 | 152 | 165 | 0.92 | 23 | 154/182 (177) | 77 |
| 2026-09-24 |  | 45.2 | 107 | 146 | 159 | 0.88 | 25 | 146/177 (176) | 75 |
| 2026-09-25 |  | 26.4 | 62 | 137 | 144 | 0.80 | 40 | 144/167 (165) | 75 |
| 2026-09-27 |  | 57.5 | 147 | 119 | 165 | 0.91 | 69 | 145/189 (189) | 72 |
| 2026-09-29 |  | 27.0 | 61 | 142 | 163 | 0.90 | 38 | 149/191 (187) (HR? min 54-58) | 76 |
| 2026-09-30 |  | 38.2 | 83 | 151 | 165 | 0.92 | 26 | 155/185 (185) | 79 |
| 2026-10-02 |  | 27.8 | 59 | 162 | 177 | 0.98 | 30 | 160/184 (183) | 82 |
| 2026-10-08 |  | 35.4 | 84 | 143 | 159 | 0.89 | 34 | 141/182 (181) | 78 |
| 2026-10-16 |  | 34.1 | 82 | 122 | 127 | 0.70 | 68 | 135/157 (155) (strap dropouts) | 77 |
| 2026-10-17 |  | 16.6 | 41 | 142 | 183 | 1.02 | 46 | 136/182 (175) (HR unusable, Pat) | 82 |
| 2026-10-30 |  | 40.0 | 98 | 127 | 144 | 0.80 | 53 | 144/173 (172) | 78 |
| 2026-10-31 |  | 61.5 | 148 | 131 | 146 | 0.81 | 62 | 144/181 (179) | 80 |
| 2026-11-01 |  | 57.7 | 138 | 131 | 152 | 0.84 | 60 | 147/188 (186) | 79 |
| 2026-11-03 | V | 8.3 | 17 | 137 | 149 | 0.83 | 71 | 149/182 (179) | 77 |
| 2026-11-04 | V | 7.8 | 15 | 167 | 175 | 0.97 | 7 | 170/187 (184) | 77 |
| 2026-11-06 | V | 17.1 | 36 | 128 | 153 | 0.85 | 83 | 154/188 (186) | 78 |
| 2026-11-06 | V | 6.4 | 13 | 131 | 157 | 0.87 | 67 | 154/185 (182) | 83 |
| 2026-11-07 | V | 30.8 | 74 | 129 | 138 | 0.77 | 76 | 148/180 (178) | 75 |
| 2026-11-08 | V | 28.4 | 60 | 128 | 135 | 0.75 | 86 | 142/172 (168) | 82 |

## 6. Runs

| Date | Name | km | Moving | Pace | HR avg/max | Splits per km (moving time) | Best 1K / mile / 5K (windowed) |
|---|---|---|---|---|---|---|---|
| 2026-10-03 | Afternoon Run | 6.35 | 34:54 | 5:30/km | 158/173 | 5:19 5:36 5:37 5:33 5:27 5:32 | 5:19 / 8:43 / 27:31 |
| 2026-10-12 | Afternoon Run | 5.03 | 27:31 | 5:28/km | 172/186 | 5:32 5:35 5:29 5:19 5:27 | 5:18 / 8:39 / 27:19 |
| 2026-10-14 | Evening Run | 7.50 | 42:16 | 5:38/km | 157/193 | 5:36 6:57 5:54 5:05 6:02 4:25 5:13 | 3:51 / 7:14 / 26:36 |
| 2026-10-18 | Afternoon Run | 2.79 | 14:09 | 5:05/km | 163/178 | 5:11 5:04 | 4:55 / 8:03 / - |
| 2026-10-23 | Afternoon Run | 6.45 | 34:59 | 5:25/km | 165/186 | 5:54 5:18 5:14 5:01 5:00 5:42 | 4:35 / 7:59 / 25:58 |
| 2026-10-26 | Lunch Run | 5.02 | 25:51 | 5:09/km | 174/187 | 5:46 4:43 4:41 4:43 5:53 | 4:34 / 7:28 / 25:45 |
| 2026-10-28 | Afternoon Run | 5.00 | 23:30 | 4:42/km | 182/196 | 5:03 4:57 4:50 4:35 4:03 | 4:03 / 6:50 / 23:30 |

Caveats: GPX-based run rows use raw GPS distance and a simple pause rule. 14 Oct: the script's best 1K (3:51) and mile (7:14) are faster than Strava's (4:01, 7:32) and its moving time (42:16) is longer than Strava's (39:06), so use Strava's numbers for that run. 28 Oct 5K: from the export GPX 5.00 km in 23:30 (matches Strava); the detailed FIT analysis (tests/28_10.fit) is in coach_notes.md.

## 7. Other data notes

- Avg watts in Strava's activities.csv for the rides 7-20 Aug (and the MTB laps) are Strava estimates, not measured; the files contain no power. First measured power: 29 Aug.
- The Garmin files also contain beat-to-beat (HRV) messages; cp_lib.hrv_quality() uses them to check HR strap artefacts; cp_lib.hr_artefact_scan() / hr_gaps() find stretches where HR cannot match the power or is missing.
- Strava-made run FIT files: the 'speed' field runs far slower than distance-derived speed; use the distance field for pacing.

## 8. After the export

Totals in the export: 46 outdoor rides, 6 virtual rides, 7 runs (last activity 8 Nov, export downloaded 9 Nov). After it (Strava connector, to be folded into the tables with the next export, Mon 16 Nov):

| Date | Type | km | Moving | Notes |
|---|---|---|---|---|
| 2026-11-10 | Run (U1) | 4.26 recorded (about 5.06 run) | 25:33 (32:44 elapsed) | 6:00/km from lap 2; phone died at 4.25 km; Strava avg HR 127 is wrong (strap flat-lined at 50 for about 10 min); valid HR from km 1.3: about 161; analysis in coach_notes.md |
| 2026-11-11 | V (KICKR + Edge/Stages) | 33.1 (MyWhoosh) | 69:36 (Edge timer 70:11) | Stages avg 119 W, NP 150; aerobic check 0 (old fan): 130 W HR 149.6, 150 W HR 160.9; one 20 s effort 506 W (Stages), a 10 s effort 516 W, the second 20 s void (KICKR power cable out); HR max 194 (clean peak about 193); RPE 5; FITs in tests/ |
| 2026-11-12 | V (KICKR + Edge/Stages) | 34.8 (MyWhoosh) | 60:00 (test part only) | 60-min FTP test: Stages 175.1 W (NP 175.3), KICKR 175.4 W; HR 171.3 avg, 172 flat from min 15, last 20 min 173.2, max 183; decoupling +1.2%; cadence 85; fan level 3, room 15 -> 19 C; RPE 7/8/9; planning FTP 175 W |

Strava bests (Ride, VirtualRide, Run) unchanged on 10 Nov; on 11 Nov new VirtualRide bests (table 2, indoor). The Garmin copy of the 11 Nov session (uploaded as an indoor 'Ride') holds the Strava Ride 15 s (527 W) and 30 s (438 W) bests: indoor Stages values, not entered in the outdoor table (outdoor 15 s 448, 30 s 397 W); the copy was deleted on 12 Nov (Ride bests 448 / 397 W again). The Garmin copy of the 12 Nov hour test briefly held the Ride 30 / 45 / 60 min bests (176 / 175 / 175 W); deleted the same evening (outdoor 171 / 163 / 157 W again). Planning FTP from 12 Nov: 175 W (the weekly table above still uses the 180 W working value; the next digest run uses 175). Virtual rides now sit on a separate Strava bike 'huh (indoor)'.

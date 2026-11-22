# History digest: Pat, cycling | running

As of 22 Nov 2026: Strava export of 22 Nov 2026 (strava_export_22_11.zip), activities to 22 Nov; FIT files from the chat and the Strava connector (bests read 22 Nov). Generated with digest_tool.py v1 (cp_lib v1.16) from data/session_context.csv; tables: data/metrics.csv, data/hci.csv, data/pmc.csv, data/bests.csv.

## 0. Context and conventions

- **Data basis** (Pat, 20 Nov): rides with power and HR and all runs from 1 Sep 2026: 31 outdoor rides, 13 indoor rides, 8 runs. Rides without power (7-20 Aug, 26 Sep) and the 29-31 Aug rides with power but no HR count only in the load history (CTL/ATL, weekly table) and the bests.
- **Source marker** after the date: (E) Strava export file, (F) FIT file from the chat (Edge; the 10 Nov run: the Strava-made FIT), (C) Strava connector only (a hand-copied reduced stream).
- **Power meters:** outdoors the Stages (left-only). Indoors the Stages via the Edge file where there is one (7 Nov and from 11 Nov), otherwise the KICKR via the MyWhoosh file (3, 4, 6 and 8 Nov; marked VK). The KICKR reads about +5 W at Z2 power and about the same at threshold; outdoor and indoor bests are kept apart.
- **FTP for load metrics:** Aug-Oct 170 W, Nov 175 W (Pat suggested Sep 165; raised to 170 because on 22 Sep he held 170.0 W for 60 min, stops excluded). Planning FTP 175 W (12 Nov hour test). Easy = at most 77% of FTP (Nov 135 W, the easy cap), tempo 77-90%, threshold+ above 90%; shares are of moving time (coasting counts as easy).
- **TSS:** rides NP-based (moving samples, coasting kept); runs rTSS = h x IF^2 x 100 with IF = normalised speed / threshold speed (5:00/km, until a run threshold test). On stop-and-go outdoor rides with sprints NP runs high (VI 1.1-1.4), so IF and TSS of many September rides read high (IF 0.95-1.10 on 1-2.5 h rides is not the true intensity). August without power: moving h x 0.75^2 x 100 (estimate, marked e).
- **CTL / ATL / TSB:** 42-day and 7-day exponential averages of the daily TSS (rides + runs), starting at 0 on 7 Aug (first Strava activity); TSB = CTL - ATL of the evening before (form going into the day). Values before mid-October still carry the zero start.
- **HCI (HR consistency index, 0-100):** how well HR matched the achieved power (rides) or pace (runs), intervals included. A pooled HR model (lag up 20 s / down 60 s plus a 15-min slow component and drift) gives each session an HR level; the index combines level (45%), within-session tracking (35%) and zone agreement (20%). Context counts partly: temperature, fan, feel, fatigue (ATL), RPE vs expected, altitude, illness give an expected HR shift; the adjusted and raw versions are blended with 35-60% weight on the adjusted one (more when the context effect is large). Scale: median 75, P10 55, P90 88, P97.5 93, P2.5 30 of the reference set (48 sessions, calibrated 2026-11-21); u = under 5 usable min or over 30% of HR blanked; - = no usable HR.
- **HRR** (1-min HR recovery, bpm): drop from the HR peak after an effort (20 s at 90%+ FTP or faster than 5:30/km) to 60 s later, only when the next 60 s are a real recovery (rolling or standing, at most 65% FTP; runs slower than 7:30/km). mod = peak in Z3-Z4, max = peak in Z5. Cells: mod; max with avg, best (one value when there was one recovery).
- **Decoupling** (%): efficiency of the first half over the second (NP/HR, runs speed/HR) without the first 10 min (runs 5) and the last 5 (runs 2); best = closest to 0. Meant for long easy rides. i = intervals or hard (distorted), s = short (under 40 min usable, runs 30), u = not enough data. Summaries use only unflagged and s values.
- **EF** (efficiency factor): NP / average HR (W per bpm); runs metres per minute / HR. Indoor and outdoor EF are not comparable (fan, meter); compare like with like.
- **HR:** cleaned before all HR metrics (manual strap ranges, artefact scan, model-based dropout pass). Cycling zones <=132 / 133-148 / 149-162 / 163-177 / >=178 (LTHR 172, max 195); running <=149 / 150-163 / 164-172 / 173-187 / >=188 (LTHR 181, max 200). HR max values are the cleaned ones; 30-s max in brackets.
- **Bests:** elapsed-based = Strava's power-curve convention (paused seconds count as 0 W); stops excluded = only moving seconds (Strava's average-power convention), shown in brackets only when it is clearly higher (3% and 4 W). W/kg at 56 kg.
- **Weather:** Open-Meteo historical forecast (hourly, Brühl and Bibbona) and the Strava export's weather fields (Leutkirch); indoor room temperature from Pat's values or the room model (start 15.5 C, rise with duration and intensity).

## 1. Score lookup (Pat's 0-100 scale)

Value of each metric at every 5th percentile of the sessions so far (higher percentile = better; decoupling by distance from 0), with the score of that percentile. The HCI is already on this scale. Weekly and monthly values are averages, so read them against these session values (averages sit closer to the middle). Columns need at least 8 values; not yet: EF run (n 5), Decoupling (abs %), rides (n 5).

| Percentile | Score | EF outdoor ride (n 26) | EF indoor ride (n 13) | HRR mod (bpm) (n 22) | HRR max (bpm) (n 25) |
|---|---|---|---|---|---|
| 95 | 91 | 1.19 | 1.15 | 38.8 | 48.0 |
| 90 | 88 | 1.16 | 1.11 | 34.6 | 42.7 |
| 85 | 86 | 1.13 | 1.07 | 33.8 | 40.7 |
| 80 | 84 | 1.13 | 1.05 | 31.4 | 39.9 |
| 75 | 82 | 1.11 | 1.03 | 31.0 | 39.0 |
| 70 | 81 | 1.10 | 1.03 | 30.3 | 39.0 |
| 65 | 79 | 1.09 | 1.02 | 29.1 | 38.4 |
| 60 | 78 | 1.08 | 1.02 | 27.3 | 37.2 |
| 55 | 76 | 1.08 | 1.02 | 26.5 | 36.8 |
| 50 | 75 | 1.08 | 1.02 | 25.6 | 35.8 |
| 45 | 73 | 1.08 | 1.01 | 24.7 | 35.4 |
| 40 | 72 | 1.06 | 1.01 | 23.9 | 35.1 |
| 35 | 70 | 1.06 | 1.00 | 22.6 | 34.5 |
| 30 | 69 | 1.05 | 1.00 | 20.2 | 33.6 |
| 25 | 67 | 1.03 | 0.99 | 18.8 | 33.0 |
| 20 | 63 | 1.02 | 0.98 | 18.0 | 32.5 |
| 15 | 59 | 1.01 | 0.96 | 16.3 | 30.8 |
| 10 | 55 | 1.00 | 0.96 | 16.0 | 29.6 |
| 5 | 38 | 1.00 | 0.93 | 12.6 | 29.1 |

## 2. All-time bests

### 2a. Outdoor rides (Stages)

| Duration | W (stops excl.) | W/kg | Date |
|---|---|---|---|
| 5s | 686 | 12.24 | 1 Nov (E) |
| 15s | 448 | 7.99 | 30 Oct (E) |
| 30s | 397 | 7.09 | 17 Oct (E) |
| 1min | 317 | 5.65 | 27 Sep (E) |
| 2min | 279 | 4.99 | 27 Sep (E) |
| 3min | 258 | 4.60 | 17 Oct (E) |
| 5min | 231 | 4.12 | 1 Nov (E) |
| 8min | 203 | 3.62 | 2 Oct (E) |
| 10min | 202 | 3.61 | 2 Oct (E) |
| 15min | 187 | 3.35 | 2 Oct (E) |
| 20min | 184 | 3.28 | 1 Nov (E) |
| 30min | 171 (184) | 3.04 | 1 Nov (E) (16 Sep) |
| 45min | 163 (176) | 2.92 | 2 Oct (E) (22 Sep) |
| 60min | 157 (170) | 2.80 | 19 Sep (E) (22 Sep) |
| 90min | 147 (156) | 2.62 | 19 Sep (E) (19 Sep) |
| 120min | 144 (151) | 2.57 | 20 Sep (E) (19 Sep) |
| 150min | 141 (150) | 2.52 | 20 Sep (E) (20 Sep) |

The values match Strava's Ride bests (read 22 Nov), except 15s 462 W (20 Nov), 30s 449 W (20 Nov), 1min 344 W (20 Nov): these come from an indoor session uploaded as a Ride (the Garmin copy of the 20 Nov trainer ride, Strava 21059503183: moved to the indoor bike on 21 Nov; Strava does not let Pat retype it as Virtual Ride, so it stays a Ride), not from outdoor efforts. The stops-excluded 20/30-min values of 16 Sep include short stops inside the window, so they overstate a continuous effort slightly.

### 2b. Indoor rides

Stages = Edge files (7 Nov and from 11 Nov); KICKR = Strava's VirtualRide bests (MyWhoosh uploads, KICKR power). The two meters agree within about 1% at threshold; short sprints read differently (cadence, sampling).

| Duration | Stages W (date) | W/kg | KICKR W (date) |
|---|---|---|---|
| 5s | 631 (20 Nov) | 11.27 | 587 (11 Nov) |
| 15s | 527 (11 Nov) | 9.41 | 534 (11 Nov) |
| 30s | 449 (20 Nov) | 8.02 | 440 (18 Nov) |
| 1min | 345 (20 Nov) | 6.15 | 328 (18 Nov) |
| 2min | 263 (14 Nov) | 4.69 | 260 (14 Nov) |
| 3min | 259 (14 Nov) | 4.62 | 260 (14 Nov) |
| 5min | 248 (15 Nov) | 4.43 | 248 (15 Nov) |
| 8min | 203 (15 Nov) | 3.62 | 203 (15 Nov) |
| 10min | 189 (15 Nov) | 3.37 | 190 (15 Nov) |
| 15min | 180 (12 Nov) | 3.21 | 180 (12 Nov) |
| 20min | 177 (12 Nov) | 3.16 | 178 (12 Nov) |
| 30min | 176 (12 Nov) | 3.14 | 176 (12 Nov) |
| 45min | 175 (12 Nov) | 3.13 | 175 (12 Nov) |
| 60min | 175 (12 Nov) | 3.13 | 174 (12 Nov) |
| 90min | 129 (17 Nov) | 2.29 | - |

## 3. Bests by month (elapsed-based, W; indoor = Stages from the Edge files)

| Month | 5s | 1min | 5min | 10min | 20min | 60min |
|---|---|---|---|---|---|---|
| 2026-08 | 473 | 273 | 210 | 182 | 154 | 137 |
| 2026-09 | 510 | 317 | 213 | 201 | 175 | 157 |
| 2026-10 | 544 | 290 | 203 | 202 | 175 | 155 |
| 2026-11 | 686 | 312 | 231 | 187 | 184 | 138 |
| 2026-11 indoor | 631 | 345 | 248 | 189 | 177 | 175 |

## 4. Weekly and monthly summaries

### 4a. Weekly load

Rides incl. indoor (V); km rides / runs; TSS = rides + runs (e = includes August estimates); avg / min / max per session; intensity shares of ride moving time (rides with power).

| Week of | Rides | Runs | km ride | km run | Moving h | TSS | TSS avg / min / max | Easy % | Tempo % | Thr+ % |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-03 | 3 | - | 36 | - | 1.4 | 78 e | 26 / 20 / 34 | - | - | - |
| 2026-08-10 | 6 | - | 112 | - | 4.6 | 260 e | 43 / 10 / 96 | - | - | - |
| 2026-08-17 | 3 | - | 69 | - | 2.7 | 149 e | 50 / 13 / 117 | - | - | - |
| 2026-08-24 | 3 | - | 34 | - | 1.4 | 142 | 47 / 3 / 88 | 53 | 7 | 40 |
| 2026-08-31 | 6 | - | 216 | - | 8.5 | 718 | 120 / 41 / 160 | 36 | 20 | 43 |
| 2026-09-07 | 5 | - | 189 | - | 7.4 | 738 | 148 / 98 / 194 | 32 | 18 | 49 |
| 2026-09-14 | 5 | - | 219 | - | 8.4 | 806 | 161 / 92 / 227 | 25 | 25 | 50 |
| 2026-09-21 | 6 | - | 200 | - | 8.1 | 720 | 144 / 75 / 230 | 35 | 21 | 45 |
| 2026-09-28 | 3 | 1 | 93 | 6.4 | 4.0 | 379 | 95 / 47 / 131 | 26 | 27 | 48 |
| 2026-10-05 | 1 | - | 35 | - | 1.4 | 124 | 124 / 124 / 124 | 28 | 34 | 38 |
| 2026-10-12 | 2 | 3 | 51 | 15.3 | 3.4 | 272 | 54 / 23 / 79 | 51 | 28 | 21 |
| 2026-10-19 | 0 | 1 | 0 | 6.5 | 0.6 | 51 | 51 / 51 / 51 | - | - | - |
| 2026-10-26 | 3 | 2 | 159 | 10.0 | 7.2 | 561 | 112 / 41 / 183 | 53 | 20 | 27 |
| 2026-11-02 | 6 (6 V) | - | 99 | - | 3.6 | 239 | 40 / 18 / 69 | 73 | 11 | 15 |
| 2026-11-09 | 4 (4 V) | 1 | 130 | 4.3 | 5.3 | 393 | 79 / 29 / 100 | 67 | 7 | 26 |
| 2026-11-16 | 5 (3 V) | - | 246 | - | 9.5 | 689 | 138 / 55 / 241 | 55 | 24 | 21 |

### 4b. Weekly form and quality

CTL, ATL and TSB at the end of the week (TSB = form going into the next day; lowest daily TSB of the week in brackets). HCI avg (range); HRR avg mod; max; decoupling best, avg, worst (unflagged rides); EF outdoor / indoor / run.

| Week of | CTL | ATL | TSB (lowest) | HCI | HRR mod; max | Decoupling | EF out / in / run |
|---|---|---|---|---|---|---|---|
| 2026-08-03 | 2 | 10 | -8 (-8) | - | - | - | - |
| 2026-08-10 | 7 | 24 | -17 (-27) | - | - | - | - |
| 2026-08-17 | 9 | 21 | -12 (-23) | - | - | - | - |
| 2026-08-24 | 11 | 26 | -15 (-15) | - | - | - | - |
| 2026-08-31 | 26 | 79 | -54 (-54) | 79 (70-88) | 26; 34 | - | 1.06 / - / - |
| 2026-09-07 | 38 | 104 | -66 (-66) | 72 (61-89) | 31; 35 | - | 1.13 / - / - |
| 2026-09-14 | 51 | 122 | -71 (-71) | 78 (61-95) | 20; 39 | - | 1.13 / - / - |
| 2026-09-21 | 59 | 116 | -57 (-62) | 73 (61-84) | 34; 36 | +0.2, +0.2, +0.2 | 1.08 / - / - |
| 2026-09-28 | 58 | 73 | -15 (-43) | 79 (53-91) | - | - | 1.08 / - / 1.12 |
| 2026-10-05 | 52 | 36 | 16 (-6) | 47 (47-47) | -; 41 | - | 1.13 / - / - |
| 2026-10-12 | 50 | 40 | 10 (8) | 62 (32-85) | - | +4.2, +4.2, +4.2 | 0.93 / - / 1.11 |
| 2026-10-19 | 43 | 19 | 25 (15) | 73 (73-73) | - | - | - / - / - |
| 2026-10-26 | 50 | 72 | -22 (-22) | 80 (71-87) | 22; 42 | - | 1.01 / - / 1.14 |
| 2026-11-02 | 47 | 51 | -4 (-13) | 59 (21-78) | - | - | - / 0.97 / - |
| 2026-11-09 | 49 | 59 | -10 (-10) | 67 (56-77) | 25; 36 | -3.4, -3.4, -3.4 | - / 1.04 / - |
| 2026-11-16 | 57 | 98 | -41 (-41) | 80 (75-93) | 21; 36 | +0.1, -2.0, -4.1 | 1.05 / 1.09 / - |

### 4c. Monthly load

| Month | Rides | Runs | km ride | km run | Moving h | TSS | TSS avg / min / max | Easy % | Tempo % | Thr+ % |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08 | 16 | - | 291 | - | 11.7 | 757 e | 47 / 3 / 128 | 42 | 14 | 43 |
| 2026-09 | 23 | - | 849 | - | 33.1 | 3079 | 140 / 41 / 230 | 32 | 22 | 47 |
| 2026-10 | 6 | 7 | 215 | 38.1 | 11.9 | 989 | 76 / 23 / 183 | 44 | 26 | 30 |
| 2026-11 | 16 (13 V) | 1 | 533 | 4.3 | 20.6 | 1494 | 88 / 18 / 241 | 61 | 16 | 22 |

### 4d. Monthly form and quality

CTL first -> last day (highest); ATL average (highest); TSB average (lowest, highest); 2026-11 is month to date.

| Month | CTL | ATL | TSB | HCI | HRR mod; max | Decoupling | EF out / in / run |
|---|---|---|---|---|---|---|---|
| 2026-08 | 1 -> 14 (14) | 20 (41) | -12 (-27, 0) | - | - | - | - |
| 2026-09 | 15 -> 60 (60) | 90 (122) | -50 (-71, -26) | 77 (61-95) | 29; 36 | +0.2, +0.2, +0.2 | 1.09 / - / - |
| 2026-10 | 59 -> 47 (60) | 41 (91) | 8 (-43, 25) | 69 (32-91) | 16; 41 | +4.2, +4.2, +4.2 | 1.04 / - / 1.12 |
| 2026-11 | 50 -> 57 (57) | 56 (98) | -6 (-22, 4) | 69 (21-93) | 24; 38 | +0.1, -2.5, -4.1 | 1.04 / 1.02 / - |

## 5. Per ride (rides with power from 1 Sep; V = indoor, Stages; VK = indoor, KICKR)

### 5a. Load

| Date (src) |  | km | Moving min | Avg W | NP | IF | Easy % | Cadence | TSS | Tempo % | Thr+ % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-01 (E) |  | 11.1 | 28 | 121 | 160 | 0.94 | 55 | 71 | 41 | 15 | 30 |
| 2026-09-02 (E) |  | 35.7 | 84 | 137 | 167 | 0.98 | 44 | 78 | 135 | 17 | 40 |
| 2026-09-03 (E) |  | 33.7 | 79 | 144 | 164 | 0.96 | 36 | 73 | 123 | 17 | 48 |
| 2026-09-05 (E) |  | 40.0 | 91 | 146 | 159 | 0.94 | 29 | 74 | 132 | 13 | 58 |
| 2026-09-06 (E) |  | 55.5 | 130 | 132 | 146 | 0.86 | 36 | 76 | 160 | 31 | 33 |
| 2026-09-08 (E) |  | 28.1 | 64 | 149 | 163 | 0.96 | 22 | 75 | 98 | 21 | 57 |
| 2026-09-09 (E) |  | 33.4 | 79 | 147 | 178 | 1.05 | 41 | 74 | 145 | 17 | 42 |
| 2026-09-10 (E) |  | 32.1 | 77 | 151 | 180 | 1.06 | 35 | 77 | 144 | 17 | 48 |
| 2026-09-12 (E) |  | 51.5 | 123 | 140 | 165 | 0.97 | 37 | 75 | 194 | 19 | 44 |
| 2026-09-13 (E) |  | 43.6 | 100 | 150 | 165 | 0.97 | 23 | 76 | 157 | 19 | 58 |
| 2026-09-15 (E) |  | 27.5 | 62 | 149 | 160 | 0.94 | 22 | 77 | 92 | 22 | 55 |
| 2026-09-16 (E) |  | 33.5 | 79 | 153 | 181 | 1.06 | 34 | 77 | 149 | 15 | 50 |
| 2026-09-17 (E) |  | 34.2 | 77 | 156 | 183 | 1.08 | 37 | 78 | 149 | 20 | 43 |
| 2026-09-19 (E) |  | 53.7 | 122 | 151 | 164 | 0.96 | 25 | 76 | 189 | 22 | 53 |
| 2026-09-20 (E) |  | 70.2 | 161 | 149 | 156 | 0.92 | 16 | 79 | 227 | 36 | 48 |
| 2026-09-22 (E) |  | 28.4 | 60 | 170 | 178 | 1.05 | 11 | 82 | 109 | 6 | 83 |
| 2026-09-23 (E) |  | 42.2 | 95 | 152 | 165 | 0.97 | 21 | 77 | 150 | 26 | 53 |
| 2026-09-24 (E) |  | 45.2 | 107 | 146 | 159 | 0.93 | 22 | 75 | 156 | 22 | 55 |
| 2026-09-25 (E) |  | 26.4 | 62 | 137 | 144 | 0.85 | 32 | 75 | 75 | 40 | 28 |
| 2026-09-27 (E) |  | 57.5 | 147 | 119 | 165 | 0.97 | 64 | 72 | 230 | 13 | 23 |
| 2026-09-29 (E) |  | 27.0 | 61 | 142 | 163 | 0.96 | 32 | 76 | 94 | 31 | 38 |
| 2026-09-30 (E) |  | 38.2 | 83 | 151 | 165 | 0.97 | 22 | 79 | 131 | 28 | 50 |
| 2026-10-02 (E) |  | 27.8 | 59 | 162 | 177 | 1.04 | 25 | 82 | 107 | 20 | 56 |
| 2026-10-08 (E) |  | 35.4 | 84 | 143 | 159 | 0.94 | 28 | 78 | 124 | 34 | 38 |
| 2026-10-16 (E) |  | 34.1 | 82 | 122 | 127 | 0.75 | 55 | 77 | 76 | 34 | 11 |
| 2026-10-17 (E) |  | 16.6 | 41 | 142 | 183 | 1.08 | 44 | 82 | 79 | 17 | 39 |
| 2026-10-30 (E) |  | 40.0 | 98 | 127 | 144 | 0.85 | 45 | 78 | 118 | 30 | 24 |
| 2026-10-31 (E) |  | 61.5 | 148 | 131 | 146 | 0.86 | 54 | 80 | 183 | 19 | 27 |
| 2026-11-01 (E) |  | 57.7 | 138 | 131 | 152 | 0.87 | 58 | 79 | 173 | 13 | 29 |
| 2026-11-03 (E) | VK | 8.4 | 17 | 137 | 149 | 0.85 | 67 | 77 | 20 | 13 | 20 |
| 2026-11-04 (E) | VK | 7.7 | 16 | 166 | 175 | 1.00 | 8 | 77 | 26 | 21 | 70 |
| 2026-11-06 (E) | VK | 6.4 | 13 | 131 | 157 | 0.89 | 66 | 83 | 18 | 4 | 30 |
| 2026-11-06 (E) | VK | 17.2 | 36 | 127 | 153 | 0.87 | 80 | 78 | 46 | 8 | 12 |
| 2026-11-07 (F) | V | 30.8 | 73 | 126 | 132 | 0.76 | 80 | 74 | 69 | 12 | 8 |
| 2026-11-08 (E) | VK | 28.4 | 60 | 127 | 135 | 0.77 | 80 | 82 | 60 | 11 | 8 |
| 2026-11-11 (F) | V | 33.1 | 69 | 120 | 150 | 0.86 | 75 | 78 | 85 | 17 | 9 |
| 2026-11-12 (F) | V | 34.8 | 60 | 175 | 176 | 1.00 | 0 | 85 | 100 | 6 | 94 |
| 2026-11-14 (F) | V | 34.1 | 101 | 118 | 132 | 0.76 | 92 | 81 | 96 | 3 | 5 |
| 2026-11-15 (F) | V | 28.5 | 60 | 116 | 158 | 0.90 | 84 | 81 | 82 | 2 | 14 |
| 2026-11-17 (F) | V | 45.8 | 90 | 129 | 142 | 0.81 | 67 | 82 | 98 | 21 | 12 |
| 2026-11-18 (F) | V | 37.9 | 80 | 130 | 150 | 0.86 | 68 | 82 | 98 | 14 | 18 |
| 2026-11-20 (F) | V | 15.5 | 35 | 134 | 170 | 0.97 | 74 | 80 | 55 | 12 | 14 |
| 2026-11-21 (F) |  | 60.4 | 146 | 145 | 157 | 0.90 | 34 | 86 | 197 | 29 | 37 |
| 2026-11-22 (F) |  | 86.5 | 216 | 131 | 143 | 0.82 | 56 | 84 | 241 | 28 | 16 |

### 5b. HR and quality

| Date (src) | HR avg/max (30 s max) | HCI | HRR mod; max | Decoupling | EF |
|---|---|---|---|---|---|
| 2026-09-01 (E) | 142/182 (176) | 83 | 26; - | u | 1.13 |
| 2026-09-02 (E) | 155/187 (185) | 70 | -; 38, 49 | +12.3 i | 1.08 |
| 2026-09-03 (E) | 156/181 (180) | 81 | -; 30, 30 | +6.1 i | 1.05 |
| 2026-09-05 (E) | 155/174 (173) | 88 | - | u | - |
| 2026-09-06 (E) | 146/174 (172) | 75 | - | +3.0 i | 1.00 |
| 2026-09-08 (E) | 161/184 (180) | 61 | - | u | - |
| 2026-09-09 (E) | 150/183 (182) | 72 | 31; 36, 41 | +15.0 i | 1.19 |
| 2026-09-10 (E) | - | 63 u | - | u | - |
| 2026-09-12 (E) | 153/187 (184) | 89 | 30; 29 | +20.9 i | 1.08 |
| 2026-09-13 (E) | 148/176 (176) | 64 | - | -0.8 i | 1.12 |
| 2026-09-15 (E) | 157/181 (180) | 77 | - | u | - |
| 2026-09-16 (E) | 153/185 (184) | 85 | -; 35 | +12.1 i | 1.18 |
| 2026-09-17 (E) | 150/184 (181) | 71 | -; 41, 44 | +13.8 i | 1.22 |
| 2026-09-19 (E) | 157/184 (182) | 95 | 20, 24; - | +12.0 i | 1.04 |
| 2026-09-20 (E) | 147/175 (172) | 61 | - | -2.9 i | 1.06 |
| 2026-09-22 (E) | 163/186 (184) | 81 | - | -1.7 i | 1.09 |
| 2026-09-23 (E) | 154/182 (177) | 84 | - | -3.2 i | 1.08 |
| 2026-09-24 (E) | 146/177 (176) | 66 | 40; - | +2.1 i | 1.09 |
| 2026-09-25 (E) | 145/166 (165) | 74 | - | +0.2 | 1.00 |
| 2026-09-27 (E) | 145/189 (189) | 61 | 31, 39; 36 | +6.2 i | 1.13 |
| 2026-09-29 (E) | 150/191 (187) | 84 | - | +5.5 i | 1.08 |
| 2026-09-30 (E) | 155/185 (185) | 87 | - | +2.7 i | 1.06 |
| 2026-10-02 (E) | 160/184 (183) | 91 | - | +3.5 i | 1.11 |
| 2026-10-08 (E) | 141/182 (181) | 47 | -; 41 | -0.3 i | 1.13 |
| 2026-10-16 (E) | 136/157 (155) | 60 | - | +4.2 | 0.93 |
| 2026-10-17 (E) | - | - | - | u | - |
| 2026-10-30 (E) | 144/173 (172) | 81 | 12; - | +7.8 i | 1.00 |
| 2026-10-31 (E) | 144/181 (179) | 87 | 19; - | +9.0 i | 1.01 |
| 2026-11-01 (E) | 148/188 (186) | 77 | 35; 42, 49 | +5.9 i | 1.03 |
| 2026-11-03 (E) | 149/182 (179) | 78 | - | u | 1.00 |
| 2026-11-04 (E) | 170/187 (184) | 21 | - | u | 1.03 |
| 2026-11-06 (E) | 162/185 (182) | 65 | - | u | 0.96 |
| 2026-11-06 (E) | 154/188 (186) | 39 | - | -9.6 i | 0.99 |
| 2026-11-07 (F) | 148/180 (178) | 74 | - | +11.8 i | 0.89 |
| 2026-11-08 (E) | 142/172 (168) | 76 | - | +6.3 i | 0.95 |
| 2026-11-11 (F) | 148/194 (188) | 68 | 27; 36, 39 | -20.2 i | 1.02 |
| 2026-11-12 (F) | 171/183 (180) | 77 | - | +1.5 i | 1.02 |
| 2026-11-14 (F) | 131/182 (181) | 69 | 30; - | -3.4 | 1.01 |
| 2026-11-15 (F) | 142/192 (189) | 56 | 22, 26; 37, 39 | +12.9 i | 1.12 |
| 2026-11-17 (F) | 139/187 (179) | 78 | 10; - | +0.1 | 1.02 |
| 2026-11-18 (F) | 142/189 (184) | 93 | 16; 37 | +29.5 i | 1.06 |
| 2026-11-20 (F) | 141/192 (190) | 79 | 27; 35 | u | 1.21 |
| 2026-11-21 (F) | 146/178 (174) | 75 | - | -3.8 i | 1.08 |
| 2026-11-22 (F) | 140/183 (182) | 78 | 25, 34; - | -4.1 | 1.02 |

## 6. Runs

### 6a. Load and pace (moving time; splits per full km)

| Date (src) | km | Moving | Pace | Norm. pace | IF | rTSS | Splits per km | Best 1K / 5K |
|---|---|---|---|---|---|---|---|---|
| 2026-10-03 (E) | 6.35 | 34:55 | 5:30/km | 5:34/km | 0.90 | 47 | 5:18 5:36 5:37 5:33 5:28 5:31 | 5:18 / 27:31 |
| 2026-10-12 (E) | 5.03 | 27:41 | 5:30/km | 5:31/km | 0.91 | 38 | 5:32 5:45 5:29 5:18 5:27 | 5:18 / 27:28 |
| 2026-10-14 (E) | 7.50 | 39:11 | 5:13/km | 5:22/km | 0.93 | 57 | 5:36 3:49 5:54 5:06 6:03 4:25 5:14 * | 3:34 / 25:08 * |
| 2026-10-18 (E) | 2.79 | 14:10 | 5:05/km | 5:05/km | 0.98 | 23 | 5:12 5:04 | 4:55 / - |
| 2026-10-23 (E) | 6.45 | 34:53 | 5:24/km | 5:19/km | 0.94 | 51 | 5:53 5:17 5:14 5:01 4:55 5:43 | 4:35 / 25:52 |
| 2026-10-26 (E) | 5.02 | 25:53 | 5:10/km | 5:06/km | 0.98 | 41 | 5:48 4:42 4:41 4:43 5:53 | 4:35 / 25:46 |
| 2026-10-28 (E) | 5.00 | 23:31 | 4:42/km | 4:41/km | 1.07 | 45 | 5:04 4:57 4:51 4:35 4:03 | 4:03 / 23:30 |
| 2026-11-10 (F) | 4.26 | 25:27 | 5:59/km | 6:00/km | 0.83 | 29 | 5:40 6:09 6:04 6:01 | 5:38 / - |

\* Reps with walking recoveries (14 Oct): the pause rule removes the walks, so single splits and the windowed bests read too fast (Strava: best 1K 4:01; moving 39:06). 10 Nov: recorded 4.26 km (phone died at 4.25 km; about 5.06 km run); HR only from min 14 (strap without contact in lap 1).

### 6b. HR and quality

| Date (src) | HR avg/max (30 s max) | HCI | HRR mod; max | Decoupling | EF |
|---|---|---|---|---|---|
| 2026-10-03 (E) | 159/173 (170) | 53 | - | +2.8 s | 1.12 |
| 2026-10-12 (E) | 172/186 (184) | 69 | - | +1.1 s | 1.03 |
| 2026-10-14 (E) | 157/193 (192) | 32 | - | -2.7 | 1.13 |
| 2026-10-18 (E) | 163/178 (176) | 85 | - | u | 1.17 |
| 2026-10-23 (E) | 162/186 (184) | 73 | - | u | - |
| 2026-10-26 (E) | 174/187 (185) | 71 | - | u | - |
| 2026-10-28 (E) | 182/196 (195) | 81 | - | -4.9 s | 1.14 |
| 2026-11-10 (F) | 160/170 (168) | 83 u | - | u | - |

Run HCI: only 8 runs, so the run reference is thin; short fast reps (14 Oct) read low partly because HR cannot catch up with the pace.

## 7. Top sessions by TSS

| # | Date (src) | Type | TSS | Moving | IF | Intensity |
|---|---|---|---|---|---|---|
| 1 | 2026-11-22 (F) | Ride | 241 | 3:36:13 | 0.82 | 143 W NP |
| 2 | 2026-09-27 (E) | Ride | 230 | 2:27:16 | 0.97 | 165 W NP |
| 3 | 2026-09-20 (E) | Ride | 227 | 2:41:01 | 0.92 | 156 W NP |
| 4 | 2026-11-21 (F) | Ride | 197 | 2:26:25 | 0.90 | 157 W NP |
| 5 | 2026-09-12 (E) | Ride | 194 | 2:03:28 | 0.97 | 165 W NP |
| 6 | 2026-09-19 (E) | Ride | 189 | 2:02:05 | 0.96 | 164 W NP |
| 7 | 2026-10-31 (E) | Ride | 183 | 2:28:13 | 0.86 | 146 W NP |
| 8 | 2026-11-01 (E) | Ride | 173 | 2:18:06 | 0.87 | 152 W NP |
| 9 | 2026-09-06 (E) | Ride | 160 | 2:09:48 | 0.86 | 146 W NP |
| 10 | 2026-09-13 (E) | Ride | 157 | 1:40:19 | 0.97 | 165 W NP |

## 8. Other data notes

- Rides without power: 7-20 Aug (12 rides; Strava's 'average watts' for them are estimates, not measured) and 26 Sep (12 min). First measured power: 29 Aug; HR strap from 1 Sep.
- HR strap problems handled in the cleaning: 5 Sep min 20-36, 10 Sep min 13-58, 29 Sep min 55-57.5, 16 Oct dropouts, 17 Oct (HR unusable), 23 Oct min 22-31 and 26 Oct min 17.3-20.7 (frozen values), 10 Nov until min 15.5 (first lap); plus dropouts found by the model pass (share in data/metrics.csv, hr_bad_pct).
- Weather of the 21 and 22 Nov rides: the export's weather columns (Strava's provider; its apparent temperature as given, 8.9 and 4.2 C).
- 12 Nov: the Edge file holds the test part only (60:03; the MyWhoosh file 61:40, 34.8 km). Indoor km: MyWhoosh distance where the Edge file has none.
- The Garmin files also contain beat-to-beat (HRV) messages; cp_lib.hrv_quality() uses them to check strap artefacts.
- Strava-made run FIT files: the 'speed' field runs far slower than distance-derived speed; use the distance field for pacing.
- Refresh: python3 digest_tool.py --export <newest export zip> --out docs/history_digest.md (add new chat FITs to tests/ and their rows to data/session_context.csv first; --calibrate about monthly).

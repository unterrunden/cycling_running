# Segments: definitions and effort archive (status 9 Nov 2026; W/kg at 56 kg since 12 Nov)

Strava segments Pat tracks, with every real effort found in his ride files. Sources: Pat's Strava values (6 and 8 Nov) for the segment
data, PR and effort count; efforts rebuilt by `segments_tool.py` v1.3 (repo) from the Strava export of 9 Nov (strava_export_09_11.zip,
46 outdoor rides; virtual rides are skipped). Rerun the tool on each new export. 16 attempted segments, 103 efforts found (all 16 counts
now equal Strava's), 46 tracked; 23 segments on the to-do list.

## How to read this
- Tracked efforts only [Pat, 7 Nov]: elapsed-based power (standing time counts as 0 W) of at least 80% of the current PR effort's power.
  Without power data (August): elapsed time at most 1.25 x the PR time on climbs (grade >= 3%), 1.08 x elsewhere (power rises with about
  speed^3 on the flat). The overview counts all efforts found; the tables list the tracked ones. Thresholds live in `segments.json`.
- Time is elapsed (as Strava). W and cadence are averaged over the recorded samples, which equals Strava's segment values when the effort
  has no auto-paused stop. With an auto-paused stop Strava counts the stop as 0 W, so its value equals the elapsed-based one; the Notes
  column then shows it ("stop 67s (elapsed-based 148 W, as Strava)"). "% of PR W" always uses the elapsed-based power. W/kg at 56 kg (Pat 12 Nov: measured; the earlier 60 kg was never weighed).
  HR from the Polar H9.
- HR is blanked where it is unusable: 17 Oct (Pat: "HR data inaccurate and not usable"); 10 Sep min 13-58 (strap gaps and dropouts, km
  about 5-22; Strava draws the missing part as a frozen line, km 7.3-13.5 in Pat's screenshot); 5 Sep min 20-36 (75-130 bpm at about
  180 W); 29 Sep min 54-58 (doubtful). "HR?" = artefact by `segments_tool.hr_flag`: 30 s+ at 200 W+ with HR at the end below 145 or
  falling, a 2-min+ effort at 200 W+ averaging below 140, or 2 min+ at 150 W+ ending below 135; "HR partial" = HR on less than 80% of
  the effort. Average HR alone is not used: HR lags, and genuine 45-s efforts at 200+ W often average only 128-142 bpm.
- Power is on the Stages scale (left-only crank meter). [mine] It probably reads about 4-10% below true power: on 8 climb efforts the
  meter energy covers 0.82-0.97 of the physics energy (median 0.90; steepest climb 0.86-0.89), and the KICKR (a hub trainer, which should
  read lower) read +4% (7 Nov, 72 min, 1 Hz) to +8% (6 Nov) above it, up to +8% at cadence below 60. Comparisons between efforts are
  unaffected.
- Validation [Strava vs tool]: 27 Sep, 9 efforts: time within 0-3 s, power within about 1 W, HR within 0.3 bpm. All 16 PR times rebuild
  (one at 195 vs 196 s). The four 30/31 Oct efforts (new in the 9 Nov export) against the connector values: Theodor-Heuss Downforce and
  Liblarer->Bleibtreu See exact in time, W and HR; Kierberger Sprint 1:46 vs 1:49; Long and windy road 19:43 vs 19:48, 148 W
  elapsed-based vs Strava 147 W, HR 158 vs 155 (the effort with the 67 s stop). Pat's August notes (Mühlenbach 2:35, Fischenich Ahoi
  4:42) match the rebuilt efforts of 7 and 11 Aug.
- New since the 27 Oct export: Long and windy road 31 Oct (19:43, 82% of the PR power: tracked); Theodor-Heuss Downforce 30 Oct (2:12,
  145 W), Liblarer->Bleibtreu See 30 Oct (4:50, 132 W) and Kierberger Sprint 31 Oct (1:46 in the file, 1:49 on Strava, 124 W) are
  below the threshold (easy rides).
- Elevations: absolute segment elevations on Strava can be offset (Kurfürsten Sprint 6-14 m, Fischenich Berg 21-72 m vs Edge 75-125 m,
  Climb zur Jugendakademie -7 to 43 m); the differences agree with Pat's Edge within about 3 m. For the to-do list (never ridden) the
  check is internal: grade x length matches the elevation difference within 1-5 m for all 20 new entries; Cäcilienhöhe and Venusberg
  "Die Mauer" show gain 0 on Strava (a data glitch; their differences, 106 and 85 m, are consistent).
- Pat marked the PRs on Mühlenbach Climb and Ab auf den Müll! as not all out, and Liblarer->Bleibtreu See as never ridden all out
  (mostly easy drive-throughs), so their 80% thresholds are low (153, 149, 162 W).

## Attempted segments
| ID | Segment | Place | km | Gain m | Grade % | Strava PR | Efforts found / Strava | Tracked | Best W (tracked) |
|---|---|---|---|---|---|---|---|---|---|
| [23234747](https://www.strava.com/segments/23234747) | Mount Phantasialand | Brühl | 1.56 | 55 | 3.5 | 3:41 | 5 / 5 | 4 | 248 |
| [38595955](https://www.strava.com/segments/38595955) | VochemBerg III | Brühl | 0.56 | 27 | 4.9 | 1:25 | 1 / 1 | 1 | 277 |
| [41002017](https://www.strava.com/segments/41002017) | Raus aus der Stadt | Brühl | 1.16 | 2 | -0.4 | 1:55 | 7 / 7 | 1 | 246 |
| [13203814](https://www.strava.com/segments/13203814) | Theodor-Heuss Downforce | Brühl | 1.27 | 0 | -2.4 | 1:43 | 19 / 19 | 3 | 255 |
| [30701495](https://www.strava.com/segments/30701495) | Fischenich Ahoi | Hürth | 1.58 | 61 | 3.5 | 4:42 | 1 / 1 | 1 | - |
| [14456798](https://www.strava.com/segments/14456798) | Kurfürsten Sprint | Brühl | 0.48 | 0 | -1.3 | 0:43 | 3 / 3 | 2 | 305 |
| [6678444](https://www.strava.com/segments/6678444) | Flammgasse Climb | Bornheim | 0.57 | 57 | 9.8 | 2:16 | 2 / 2 | 1 | 270 |
| [42273304](https://www.strava.com/segments/42273304) | Kierberger Sprint | Brühl | 0.74 | 4 | -0.2 | 1:09 | 13 / 13 | 4 | 301 |
| [27969520](https://www.strava.com/segments/27969520) | Mühlenbach Climb | Brühl | 0.77 | 33 | 4.2 | 2:27 | 3 / 3 | 2 | 192 |
| [8001608](https://www.strava.com/segments/8001608) | Die UtkDoe Challenge | Kerpen | 0.94 | 0 | -0.9 | 1:16 | 9 / 9 | 4 | 283 |
| [10822662](https://www.strava.com/segments/10822662) | Ab auf den Müll! | Erftstadt | 1.79 | 2 | -0.5 | 3:16 | 13 / 13 | 9 | 211 |
| [17867626](https://www.strava.com/segments/17867626) | Long and windy road - Formtest | Erftstadt | 7.87 | 39 | 0.5 | 15:55 | 2 / 2 | 2 | 182 |
| [13164514](https://www.strava.com/segments/13164514) | Otto-Wels-Sprint | Brühl | 1.70 | 6 | -0.6 | 3:12 | 4 / 4 | 3 | 207 |
| [8327378](https://www.strava.com/segments/8327378) | Liblarer->Bleibtreu See | Erftstadt | 1.90 | 17 | 0.9 | 3:53 | 17 / 17 | 5 | 202 |
| [21410880](https://www.strava.com/segments/21410880) | Fischenich Berg Gleise -> Ampel | Hürth | 0.85 | 42 | 4.9 | 2:23 | 2 / 2 | 2 | 261 |
| [979311](https://www.strava.com/segments/979311) | Fischenich Berg | Hürth | 1.05 | 51 | 4.9 | 2:55 | 2 / 2 | 2 | 257 |

## Not attempted yet (Pat's list, 8 Nov; climbs mostly Bonn / Bornheim / Siebengebirge, one Ahr valley target)
| ID | Segment | Place | km | Gain m | Grade % | Elev. diff m | Cat | Note |
|---|---|---|---|---|---|---|---|---|
| [20763365](https://www.strava.com/segments/20763365) | Von Brühl nach Hürth | Brühl | 5.94 | 34 | 0.1 | 12 | - | min/max elevation implausible (Pat) |
| [12834459](https://www.strava.com/segments/12834459) | Bergstraße vollständig | Bonn | 0.82 | 95 | 11.6 | 95 | 4 |  |
| [26322407](https://www.strava.com/segments/26322407) | Buschgasse Brühl Road | Brühl | 0.56 | 35 | 6.2 | 35 | - |  |
| [8704202](https://www.strava.com/segments/8704202) | Vochem | Brühl | 1.44 | 50 | 3.0 | 43 | - | the relevant Vochem segment (Pat 8 Nov; replaces Vochem Climb 9213838) |
| [13840678](https://www.strava.com/segments/13840678) | Climb zur Jugendakademie | Bornheim | 0.56 | 49 | 8.7 | 49 | - | Strava low/high elevation offset (negative low) |
| [9512280](https://www.strava.com/segments/9512280) | Quellenstraße | Bad Godesberg | 0.34 | 30 | 8.7 | 30 | - |  |
| [2112959](https://www.strava.com/segments/2112959) | Cäcilienhöhe | Bad Godesberg | 1.63 | 0 (?) | 6.5 | 106 | 4 | Strava shows gain 0 (data glitch); grade x length = 106 m matches the elevation difference |
| [10985999](https://www.strava.com/segments/10985999) | Kirchberg Climb | Bad Godesberg | 0.54 | 64 | 11.6 | 64 | - |  |
| [752100](https://www.strava.com/segments/752100) | Drachenfelsstraße 47 Climb | Königswinter | 2.28 | 168 | 7.3 | 168 | 3 |  |
| [1557793](https://www.strava.com/segments/1557793) | Am Heidchen 28 Climb | Königswinter | 1.09 | 108 | 9.9 | 108 | 4 |  |
| [9587957](https://www.strava.com/segments/9587957) | Königswinter Bhf. -> Petersberg | Königswinter | 3.72 | 297 | 7.0 | 259 | 3 | gain 297 m > difference 259 m: includes dips |
| [752098](https://www.strava.com/segments/752098) | Petersberg 1 Climb | Königswinter | 2.10 | 178 | 8.7 | 178 | 3 | verified segment (Strava) |
| [15304012](https://www.strava.com/segments/15304012) | Pech nach Gimmersdorf, Grüner Weg | Wachtberg | 1.86 | 70 | 3.7 | 70 | - | the Strava name carries a "⇘" arrow: check the direction |
| [2212734](https://www.strava.com/segments/2212734) | Hummerichsweg Climb | Bad Godesberg | 1.23 | 89 | 6.9 | 84 | 4 |  |
| [793241](https://www.strava.com/segments/793241) | Annaberger Hof Climb | Bad Godesberg | 1.49 | 103 | 6.9 | 103 | 4 |  |
| [7880047](https://www.strava.com/segments/7880047) | Rankenberg Auffahrt | Bornheim | 1.51 | 79 | 5.1 | 78 | - |  |
| [27994416](https://www.strava.com/segments/27994416) | Kardorfer Junggesellenfest | Bornheim | 1.18 | 77 | 6.5 | 77 | - |  |
| [1062584](https://www.strava.com/segments/1062584) | Jennerstraße Climb | Bornheim | 0.54 | 54 | 9.6 | 54 | - |  |
| [1778331](https://www.strava.com/segments/1778331) | Stationsweg Kreuzberg | Bonn | 0.44 | 60 | 13.5 | 60 | - |  |
| [11772652](https://www.strava.com/segments/11772652) | Lengsdorf Climb | Hardtberg (Bonn) | 0.39 | 35 | 9.0 | 35 | - |  |
| [2145413](https://www.strava.com/segments/2145413) | Venusberg "Die Mauer" | Bonn | 0.61 | 0 (?) | 13.8 | 85 | 4 | Strava shows gain 0 (data glitch); grade x length = 84 m matches the difference |
| [2341690](https://www.strava.com/segments/2341690) | Wallfahrtsweg | Bonn | 0.85 | 82 | 9.6 | 82 | 4 |  |
| [14357385](https://www.strava.com/segments/14357385) | UP to the clouds | Ahrbrück | 9.65 | 382 | 3.8 | 370 | 2 | Pat: "ultimate challenge"; Ahr valley, a long-ride target |

## Effort archive (tracked efforts, newest first)

### Mount Phantasialand (23234747), 1.56 km, 55 m, 3.5 %
| Date | Time | Rank | km/h | W | W/kg | % of PR W | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-27 15:49 | 3:41 | 1 | 25.6 | 248 | 4.43 | 100 | 88 | 182/189 |  |
| 2026-08-29 19:30 | 4:03 | 3 | 23.2 | 219 | 3.91 | 88 | 87 | -/- |  |
| 2026-08-19 15:44 | 3:45 | 2 | 25.1 | - | - | - | - | -/- |  |
| 2026-08-09 19:29 | 4:10 | 4 | 22.6 | - | - | - | - | -/- |  |
1 more effort(s) below the tracking threshold not listed.

### VochemBerg III (38595955), 0.56 km, 27 m, 4.9 %
| Date | Time | Rank | km/h | W | W/kg | % of PR W | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-27 16:41 | 1:25 | 1 | 23.6 | 277 | 4.94 | 100 | 84 | 178/187 |  |

### Raus aus der Stadt (41002017), 1.16 km, 2 m, -0.4 %
| Date | Time | Rank | km/h | W | W/kg | % of PR W | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-27 18:10 | 1:55 | 1 | 36.5 | 246 | 4.40 | 100 | 91 | 174/182 |  |
6 more effort(s) below the tracking threshold not listed.

### Theodor-Heuss Downforce (13203814), 1.27 km, 0 m, -2.4 %
| Date | Time | Rank | km/h | W | W/kg | % of PR W | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-27 17:48 | 1:43 | 1 | 44.5 | 255 | 4.56 | 100 | 96 | 179/184 |  |
| 2026-09-22 17:14 | 1:48 | 3 | 42.1 | 229 | 4.09 | 90 | 93 | 175/180 | stop 18s |
| 2026-08-30 18:54 | 1:46 | 2 | 43.3 | 209 | 3.72 | 82 | 100 | -/- |  |
16 more effort(s) below the tracking threshold not listed.

### Fischenich Ahoi (30701495), 1.58 km, 61 m, 3.5 % - no power or HR yet
| Date | Time | Rank | km/h | W | W/kg | % of PR W | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-11 17:44 | 4:42 | 1 | 19.8 | - | - | - | - | -/- |  |

### Kurfürsten Sprint (14456798), 0.48 km, 0 m, -1.3 % - segment min/max elevation implausible (Pat)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-27 17:07 | 0:43 | 1 | 40.5 | 305 | 5.45 | 100 | 96 | 169/177 |  |
| 2026-08-12 12:55 | 0:44 | 2 | 40.0 | - | - | - | - | -/- |  |
1 more effort(s) below the tracking threshold not listed.

### Flammgasse Climb (6678444), 0.57 km, 57 m, 9.8 %
| Date | Time | Rank | km/h | W | W/kg | % of PR W | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-27 16:04 | 2:16 | 1 | 14.9 | 270 | 4.82 | 100 | 79 | 184/189 |  |
1 more effort(s) below the tracking threshold not listed.

### Kierberger Sprint (42273304), 0.74 km, 4 m, -0.2 %
| Date | Time | Rank | km/h | W | W/kg | % of PR W | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-17 18:24 | 1:14 | 3 | 36.1 | 277 | 4.95 | 102 | 98 | -/- | HR data inaccurate and not usable (Pat: 17 Oct, derailleur failure ride) |
| 2026-10-02 16:28 | 1:22 | 5 | 32.9 | 236 | 4.22 | 87 | 84 | 171/182 |  |
| 2026-09-29 19:28 | 1:10 | 2 | 38.4 | 301 | 5.38 | 111 | 95 | 178/191 |  |
| 2026-09-27 18:48 | 1:09 | 1 | 38.9 | 270 | 4.83 | 100 | 93 | 173/180 |  |
9 more effort(s) below the tracking threshold not listed.

### Mühlenbach Climb (27969520), 0.77 km, 33 m, 4.2 % - not nearly all out (Pat)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-17 17:43 | 2:27 | 1 | 19.0 | 192 | 3.42 | 100 | 83 | -/- | HR data inaccurate and not usable (Pat: 17 Oct, derailleur failure ride) |
| 2026-08-07 16:18 | 2:35 | 2 | 18.0 | - | - | - | - | -/- |  |
1 more effort(s) below the tracking threshold not listed.

### Die UtkDoe Challenge (8001608), 0.94 km, 0 m, -0.9 %
| Date | Time | Rank | km/h | W | W/kg | % of PR W | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-08 18:04 | 1:16 | 1 | 44.2 | 283 | 5.05 | 100 | 94 | 175/182 |  |
| 2026-10-08 17:49 | 1:18 | 2 | 43.0 | 253 | 4.52 | 90 | 93 | 155/178 |  |
| 2026-09-30 18:15 | 1:25 | 3 | 39.2 | 253 | 4.51 | 89 | 93 | 179/185 |  |
| 2026-09-15 16:31 | 1:34 | 5 | 35.9 | 231 | 4.12 | 82 | 87 | 173/181 |  |
5 more effort(s) below the tracking threshold not listed.

### Ab auf den Müll! (10822662), 1.79 km, 2 m, -0.5 % - not all out (Pat)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-02 16:07 | 3:19 | 3 | 32.6 | 192 | 3.43 | 103 | 88 | 169/177 |  |
| 2026-09-30 18:21 | 3:31 | 7 | 30.7 | 150 | 2.68 | 80 | 81 | 154/160 |  |
| 2026-09-23 19:05 | 3:46 | 10 | 28.6 | 151 | 2.69 | 81 | 75 | 153/156 |  |
| 2026-09-22 16:59 | 3:15 | 1 | 33.3 | 186 | 3.32 | 100 | 85 | 162/169 |  |
| 2026-09-17 17:19 | 3:24 | 6 | 31.8 | 175 | 3.13 | 94 | 83 | 162/166 |  |
| 2026-09-17 17:09 | 3:23 | 5 | 32.0 | 194 | 3.47 | 105 | 83 | 161/178 |  |
| 2026-09-17 17:00 | 3:16 | 2 | 33.0 | 211 | 3.76 | 113 | 86 | 167/179 |  |
| 2026-09-17 16:49 | 3:19 | 3 | 32.5 | 203 | 3.62 | 109 | 85 | 160/178 |  |
| 2026-09-15 16:37 | 3:32 | 8 | 30.7 | 166 | 2.97 | 89 | 84 | 169/173 |  |
4 more effort(s) below the tracking threshold not listed.

### Long and windy road - Formtest (17867626), 7.87 km, 39 m, 0.5 %
| Date | Time | Rank | km/h | W | W/kg | % of PR W | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-11-01 14:52 | 15:55 | 1 | 29.7 | 182 | 3.24 | 100 | 86 | 172/178 |  |
| 2026-10-31 15:39 | 19:43 | 2 | 23.9 | 157 | 2.80 | 82 | 86 | 158/170 | stop 67s (elapsed-based 148 W, as Strava) |

### Otto-Wels-Sprint (13164514), 1.70 km, 6 m, -0.6 % - PR on the very first road ride (Pat)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-20 16:42 | 3:16 | 3 | 30.7 | 173 | 3.08 | - | 77 | 155/160 |  |
| 2026-09-10 19:50 | 3:13 | 2 | 31.3 | 207 | 3.69 | - | 84 | 167/173 |  |
| 2026-08-07 16:01 | 3:12 | 1 | 31.4 | - | - | - | - | -/- |  |
1 more effort(s) below the tracking threshold not listed.

### Liblarer->Bleibtreu See (8327378), 1.90 km, 17 m, 0.9 % - mostly easy drive-throughs, never all out (Pat)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-02 16:17 | 3:53 | 1 | 29.4 | 202 | 3.61 | 100 | 88 | 171/175 |  |
| 2026-09-22 17:08 | 4:09 | 5 | 27.5 | 187 | 3.34 | 93 | 82 | 166/169 |  |
| 2026-09-12 17:31 | 3:59 | 3 | 28.6 | 182 | 3.24 | 90 | 82 | 169/178 |  |
| 2026-09-05 20:00 | 4:00 | 4 | 28.6 | 180 | 3.21 | 89 | 76 | 166/169 |  |
| 2026-09-05 19:34 | 3:58 | 2 | 28.7 | 180 | 3.21 | 89 | 76 | -/- | HR unusable: 5 Sep min 20-36 (HR 75-130 at about 180 W, found 8 Nov) |
12 more effort(s) below the tracking threshold not listed.

### Fischenich Berg Gleise -> Ampel (21410880), 0.85 km, 42 m, 4.9 % - PR HR unusable (17 Oct); Pat: ~173 avg / ~182 max, not trustworthy
| Date | Time | Rank | km/h | W | W/kg | % of PR W | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-17 18:04 | 2:23 | 1 | 20.8 | 261 | 4.65 | 100 | 87 | -/- | HR data inaccurate and not usable (Pat: 17 Oct, derailleur failure ride) |
| 2026-09-10 19:01 | 2:38 | 2 | 18.9 | 223 | 3.97 | 85 | 68 | -/- | HR unusable: strap gaps and dropouts 10 Sep min 13-58 (km about 5-22; Pat's screenshot: frozen line km 7.3-13.5 = missing data, drop to 0 at km 13.6) |

### Fischenich Berg (979311), 1.05 km, 51 m, 4.9 % - Strava low/high elevation 21-72 m is offset by about -54 m (Edge 75-125 m; Gleise -> Ampel on the same climb matches the Edge within 2 m); the 51 m difference is right. PR HR unusable (17 Oct)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-17 18:04 | 2:55 | 1 | 21.6 | 257 | 4.59 | 100 | 88 | -/- | HR data inaccurate and not usable (Pat: 17 Oct, derailleur failure ride) |
| 2026-09-10 19:01 | 3:20 | 2 | 19.0 | 216 | 3.85 | 84 | 71 | -/- | HR unusable: strap gaps and dropouts 10 Sep min 13-58 (km about 5-22; Pat's screenshot: frozen line km 7.3-13.5 = missing data, drop to 0 at km 13.6) |

## Observations [mine]
- Best relative efforts: Kierberger Sprint 29 Sep 301 W for 1:10 (5.4 W/kg, 111% of the PR power, HR to 191, 1 s off the PR set at
  270 W); Flammgasse Climb 27 Sep 270 W for 2:16 at 79 rpm (HR 184/189); Fischenich Berg Gleise -> Ampel 17 Oct 261 W for 2:23 (4.7 W/kg);
  Mount Phantasialand 27 Sep 248 W for 3:41 (HR 183/189).
- 27 Sep (the end of the 4-week sprint plan) holds 7 of the 16 PRs; 17 Oct holds 3 (Mühlenbach and both Fischenich segments, with unusable HR); the other 6 are spread
  over 7 Aug - 1 Nov. (Earlier versions said 17 Oct held 4: the Kierberger effort that day is rank 3, not the PR.)
- HR max 191 bpm on 29 Sep at the end of a 75 s effort above 300 W: a smooth rise, not a spike, and Pat's highest strap HR (cycling max
  set to 193).
- Long and windy road: 31 Oct (endurance ride, 148 W elapsed-based incl. a 67 s stop) vs the 1 Nov 4DP-week PR (182 W, 15:55): the
  segment works as a repeatable 16-20 min flat benchmark, but it is wind-dependent.
- Most ridden: Theodor-Heuss Downforce (19 efforts on Strava, downhill), Liblarer->Bleibtreu See (17, flat, mostly easy) and Ab auf den
  Müll! (13, flat): good for tracking but wind-dependent. The climbs (Mount Phantasialand, Flammgasse, Mühlenbach, the two Fischenich
  segments) are the least wind-sensitive benchmarks.
- The to-do climbs reach 13.5-13.8% (Stationsweg Kreuzberg, Venusberg "Die Mauer"). With 34x34 as the lowest gear (2.10 m wheel,
  model 72 kg) that is about 56 rpm at 200 W, 70 rpm at 250 W and 83 rpm at 300 W: fine all out, a grind at easier power.

## Updating
1. New export in the repo -> `python3 segments_tool.py` -> new `segments_archive.csv` (tracked efforts) and these tables; check the
   found counts against Strava.
2. New segment: Pat sends the link and Strava values (distance, gain, grade, low/high elevation, PR time, W, cadence, HR avg/max,
   efforts, category) -> `fingerprint()` locates the PR ride -> `add_segment()` -> commit `segments.json`. A to-do segment gets its
   reference line from the first ride over it (same fingerprint once Pat sends the PR values).
3. A PR on a segment without power/HR: also give the elevation difference; check the effort count.
4. Pat reports a ride with bad HR -> add it to `hr_unusable` in `segments.json` (whole ride, or a minute range); `cp.hr_artefact_scan` and
   `cp.hr_gaps` find candidates.
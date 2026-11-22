# Segments: definitions and effort archive (status 22 Nov 2026: efforts to 22 Nov; W/kg at 56 kg)

Strava segments Pat tracks, with every effort found in his ride files. Sources: Pat's Strava values (6, 8 and 22 Nov) for the segment data, PR and
effort count; efforts rebuilt by `segments_tool.py` v1.5 from the Strava export of 22 Nov (strava_export_22_11.zip, 48 outdoor rides; virtual
rides and indoor Edge files are skipped). Rerun the tool on each new export. 35 attempted segments, 158 efforts found (every count equals Strava's),
53 tracked; 36 segments on the to-do list.

## How to read this
- Tracking [Pat 7 Nov, 22 Nov; v1.5]: an effort with power is tracked when its elapsed-based power (standing time counts as 0 W) is at least
  80% of the PR effort's power, at least 70% of his ability at that duration (the capability curve below) and at least 90% of FTP (158 W at
  175 W), so easy passes and long Z2 stretches drop out even when they are the PR. Efforts without power (August) count by time: at most 1.25 x
  (climbs, grade >= 3%) or 1.08 x (elsewhere) the time of the fastest tracked powered effort; if the segment has powered efforts but none is
  tracked, only no-power efforts faster than all of them; with no powered effort at all, against the PR time. Segments marked counted-only
  (Erdbeer-Radweg [Pat]) keep their count but list nothing. Counts always include every effort, so they match Strava.
- Listing [Pat 22 Nov]: at most 10 tracked efforts per segment (the fastest 8 and the slowest 2); the rest is summarised under the table.
- Ability (capability curve, 2026-11-22; max of his outdoor and indoor Stages bests): 5 s 686 W, 15 s 527 W, 30 s 449 W, 1 min 345 W, 2 min 279 W, 3 min 259 W, 5 min 248 W, 8 min 203 W, 10 min 202 W, 15 min 187 W, 20 min 184 W, 30 min 176 W, 45 min 175 W, 60 min 175 W. 'Best vs ability' and
  '% of ability' = elapsed-based power / this curve at the effort's duration; update the curve with new bests (`segments.json` 'capability').
- Time is elapsed (as Strava). W and cadence are averaged over the recorded samples, which equals Strava's segment values when the effort
  has no auto-paused stop; with a stop Strava counts it as 0 W (the Notes column shows the elapsed-based value). '% of PR W' uses the
  elapsed-based power. W/kg at 56 kg [Pat 12 Nov, measured; about 56 kg on average to 22 Nov]. HR from the Polar H9.
- HR is blanked where it is unusable: 17 Oct [Pat: 'HR data inaccurate and not usable']; 10 Sep min 13-58 (strap gaps and dropouts);
  5 Sep min 20-36 (75-130 bpm at about 180 W); 29 Sep min 54-58 (doubtful). 'HR?' = artefact by `segments_tool.hr_flag`: 30 s+ at 200 W+
  with HR at the end below 145 or falling, a 2-min+ effort at 200 W+ averaging below 140, or 2 min+ at 150 W+ ending below 135; 'HR partial'
  = HR on less than 80% of the effort. Average HR alone is not used: HR lags 30-90 s, so genuine 45-s efforts often average 128-142 bpm.
- Power is on the Stages scale (left-only crank meter). [mine] Physics check of 8 outdoor climbs (6 Nov, 68 kg system): the Stages reads
  about 0-5% below the physics estimate (meter / physics energy median about 0.95); the KICKR reads +2 to +6 W at Z2 and the same at
  threshold (settled 14-20 Nov). Comparisons between efforts are unaffected.
- Validation [Strava vs tool]: 27 Sep, 9 efforts: time within 0-3 s, power within about 1 W, HR within 0.3 bpm; all PR times rebuild within
  1-3 s (RM Phanta go: the tool's fastest is 2:19 on 27 Sep, Strava's PR 2:20 on 19 Aug). 21/22 Nov against the connector's efforts:
  Erp-Friesheim 303 s / 156 W / HR 149 vs 303 s / 156.3 W / 148.6; Metternich Climb 94 s / 236 W vs 94 s / 235.5 W; Swister Turm runter
  100 vs 100 s; Sprint von A553 zur A61 298 vs 299 s; Kurfürsten Sprint lang 108 vs 108 s; RM Phanta go 202 vs 201 s. One difference:
  Ortsschildsprint Brühl City on 22 Nov is 2:20 in the file with a 60 s auto-paused stop, 1:18 on Strava (Strava leaves that paused minute out).
- Römersprint on 21 Nov: ridden in reverse (the segment's end at ride km 57.9, its start at km 58.6), so no effort; Pat saw it missing on Strava.
- Elevations: absolute segment elevations on Strava can be offset (Kurfürsten Sprint 6-14 m, Fischenich Berg 21-72 m vs Edge 75-125 m,
  Climb zur Jugendakademie -7 to 43 m, Sprint von A553 zur A61 32-42 m); the differences agree with the Edge within about 3 m. For the to-do
  list the check is internal: grade x length matches the elevation difference within 1-3 m for every entry; Cäcilienhöhe, Venusberg "Die Mauer"
  and Wand von Merten show gain 0 on Strava (data glitches; their differences are consistent). [Pat 22 Nov] Grades of the segments in this area
  are often sketchy (Strava's grade is an average over the segment).
- Pat marked as not all out: the PRs on Mühlenbach Climb and Ab auf den Müll!, Liblarer->Bleibtreu See (mostly easy drive-throughs) and every
  segment added on 22 Nov (none of those PRs were all out).

## Attempted segments
| ID | Segment | Place | km | Gain m | Grade % | Strava PR | Efforts | Tracked | Best tracked W | Best vs ability |
|---|---|---|---|---|---|---|---|---|---|---|
| [23234747](https://www.strava.com/segments/23234747) | Mount Phantasialand | Brühl | 1.56 | 55 | 3.5 | 3:41 | 6 | 4 | 248 | 97% |
| [38595955](https://www.strava.com/segments/38595955) | VochemBerg III | Brühl | 0.56 | 27 | 4.9 | 1:25 | 1 | 1 | 277 | 89% |
| [41002017](https://www.strava.com/segments/41002017) | Raus aus der Stadt | Brühl | 1.16 | 2 | -0.4 | 1:55 | 7 | 1 | 246 | 87% |
| [13203814](https://www.strava.com/segments/13203814) | Theodor-Heuss Downforce | Brühl | 1.27 | 0 | -2.4 | 1:43 | 19 | 3 | 255 | 87% |
| [30701495](https://www.strava.com/segments/30701495) | Fischenich Ahoi | Hürth | 1.58 | 61 | 3.5 | 4:42 | 1 | 1 | - | - |
| [14456798](https://www.strava.com/segments/14456798) | Kurfürsten Sprint | Brühl | 0.48 | 0 | -1.3 | 0:43 | 4 | 2 | 305 | 77% |
| [6678444](https://www.strava.com/segments/6678444) | Flammgasse Climb | Bornheim | 0.57 | 57 | 9.8 | 2:16 | 2 | 1 | 270 | 99% |
| [42273304](https://www.strava.com/segments/42273304) | Kierberger Sprint | Brühl | 0.74 | 4 | -0.2 | 1:09 | 13 | 4 | 301 | 91% |
| [27969520](https://www.strava.com/segments/27969520) | Mühlenbach Climb | Brühl | 0.77 | 33 | 4.2 | 2:27 | 3 | 2 | 192 | 71% |
| [8001608](https://www.strava.com/segments/8001608) | Die UtkDoe Challenge | Kerpen | 0.94 | 0 | -0.9 | 1:16 | 9 | 4 | 283 | 88% |
| [10822662](https://www.strava.com/segments/10822662) | Ab auf den Müll! | Erftstadt | 1.79 | 2 | -0.5 | 3:16 | 13 | 5 | 211 | 82% |
| [17867626](https://www.strava.com/segments/17867626) | Long and windy road - Formtest | Erftstadt | 7.87 | 39 | 0.5 | 15:55 | 2 | 1 | 182 | 97% |
| [13164514](https://www.strava.com/segments/13164514) | Otto-Wels-Sprint | Brühl | 1.70 | 6 | -0.6 | 3:12 | 4 | 2 | 207 | 80% |
| [8327378](https://www.strava.com/segments/8327378) | Liblarer->Bleibtreu See | Erftstadt | 1.90 | 17 | 0.9 | 3:53 (02.10.) | 17 | 5 | 202 | 80% |
| [21410880](https://www.strava.com/segments/21410880) | Fischenich Berg Gleise -> Ampel | Hürth | 0.85 | 42 | 4.9 | 2:23 (17.10.) | 2 | 2 | 261 | 97% |
| [979311](https://www.strava.com/segments/979311) | Fischenich Berg | Hürth | 1.05 | 51 | 4.9 | 2:55 (17.10.) | 2 | 2 | 257 | 98% |
| [13395002](https://www.strava.com/segments/13395002) | Such dir ein schnelles Hinterrad! | Kerpen | 0.90 | 0 | -2.8 | 1:18 (30.10.) | 3 | 0 | - | - |
| [7228295](https://www.strava.com/segments/7228295) | Erp-Friesheim | Erftstadt | 2.52 | 2 | -0.1 | 5:03 (21.11.) | 3 | 0 | - | - |
| [27440949](https://www.strava.com/segments/27440949) | L33 ost | Erftstadt | 2.47 | 3 | -0.1 | 4:31 (20.09.) | 3 | 0 | - | - |
| [17985090](https://www.strava.com/segments/17985090) | Knallgas runter | Bornheim | 0.81 | 0 | -7.2 | 1:02 (21.11.) | 2 | 0 | - | - |
| [18357516](https://www.strava.com/segments/18357516) | Römersprint | Brühl | 0.62 | 0 | -0.3 | 1:08 (10.09.) | 9 | 0 | - | - |
| [28467890](https://www.strava.com/segments/28467890) | Metternich Climb | Weilerswist | 0.35 | 29 | 8.2 | 1:34 (22.11.) | 1 | 1 | 236 | 78% |
| [3171185](https://www.strava.com/segments/3171185) | Mur von Metternich | Weilerswist | 0.60 | 27 | 4.5 | 2:22 (22.11.) | 1 | 1 | 191 | 71% |
| [32958179](https://www.strava.com/segments/32958179) | Nörvenich 6k TT | Nörvenich | 6.13 | 2 | -0.4 | 13:14 (22.11.) | 1 | 0 | - | - |
| [4462552](https://www.strava.com/segments/4462552) | Nörvenich 5km TT | Nörvenich | 4.92 | 2 | -0.4 | 10:56 (22.11.) | 1 | 0 | - | - |
| [10165958](https://www.strava.com/segments/10165958) | Swister Turm runter | Weilerswist | 0.98 | 3 | -4.0 | 1:24 (29.09.) | 2 | 0 | - | - |
| [14573652](https://www.strava.com/segments/14573652) | Sprint von A553 zur A61 | Erftstadt | 0.98 | 10 | 1.0 | 2:09 (20.09.) | 3 | 0 | - | - |
| [7715142](https://www.strava.com/segments/7715142) | Zum Swister Turm | Weilerswist | 0.47 | 23 | 5.0 | 1:27 (08.09.) | 5 | 3 | 228 | 74% |
| [41393364](https://www.strava.com/segments/41393364) | Ortsschildsprint Brühl City | Brühl | 0.50 | 0 | -0.3 | 1:01 (27.09.) | 2 | 0 | - | - |
| [17478206](https://www.strava.com/segments/17478206) | Mit Schwung in die Stadt | Brühl | 0.48 | 2 | -2.1 | 0:43 (30.08.) | 4 | 0 | - | - |
| [17971906](https://www.strava.com/segments/17971906) | RM Phanta go | Brühl | 0.92 | 42 | 4.5 | 2:20 (19.08.) | 6 | 5 | 255 | 94% |
| [31536033](https://www.strava.com/segments/31536033) | Kurfürsten Sprint lang | Brühl | 0.82 | 0 | -0.7 | 1:23 (12.08.) | 4 | 1 | - | - |
| [40613488](https://www.strava.com/segments/40613488) | Eisenwerk Brühl | Brühl | 0.55 | 0 | 0.0 | 1:07 (17.08.) | 1 | 1 | - | - |
| [9963429](https://www.strava.com/segments/9963429) | Erdbeer-Radweg | Erftstadt | 1.13 | 0 | 0.0 | 6:14 (22.11.) | 1 | 0 | - | - |
| [35140485](https://www.strava.com/segments/35140485) | No10 revers | Brühl | 0.63 | 0 | 0.0 | 1:15 (22.11.) | 1 | 1 | 264 | 81% |

## Not attempted yet (Pat's lists of 8 and 22 Nov; climbs mostly Bonn / Bornheim / Siebengebirge, one Ahr valley target)
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
| [861775](https://www.strava.com/segments/861775) | Rampe nach Hemmerich | Bornheim | 1.28 | 75 | 5.8 | 75 | - | added 22 Nov; 83-158 m; [mine, tentative] probably Kardorf -> Burg Hemmerich (quäldich: up to 10-13% in Hemmerich) |
| [18864527](https://www.strava.com/segments/18864527) | last 13% | Bornheim | 0.32 | 16 | 5.0 (?) | 16 | - | added 22 Nov; 144-160 m; Pat: Strava grade inaccurate; 5% matches the 16 m, so '13%' is probably a short steepest part |
| [34919991](https://www.strava.com/segments/34919991) | Das Beste kommt meistens zum Schluss | Bornheim | 0.54 | 50 | 9.2 | 50 | - | added 22 Nov; 107-157 m |
| [4712252](https://www.strava.com/segments/4712252) | Wand von Merten | Bornheim | 0.73 | 0 (?) | 7.4 | 55 | - | added 22 Nov; 95-151 m; Strava gain 0 (glitch, as Pat noted); [mine, tentative] probably Sommersberg from Merten (climbfinder: 7.4%, steepest 100 m 14.1%) |
| [12240283](https://www.strava.com/segments/12240283) | Pehler Hülle Climb | Brühl | 0.29 | 17 | 5.8 | 17 | - | added 22 Nov; 76-93 m |
| [12327935](https://www.strava.com/segments/12327935) | Badorfer Rampe | Brühl | 0.23 | 12 | 5.0 | 12 | - | added 22 Nov; 88-99 m |
| [12240330](https://www.strava.com/segments/12240330) | Steingasse > Kirche Climb | Brühl | 0.76 | 36 | 4.6 | 36 | - | added 22 Nov; 73-109 m |
| [26852206](https://www.strava.com/segments/26852206) | Auf der Höhe der Zeit | Brühl | 0.93 | 44 | 4.7 | 44 | - | added 22 Nov; 79-122 m |
| [30876139](https://www.strava.com/segments/30876139) | Eckdorfer Rampe | Brühl | 0.76 | 28 | 3.5 | 28 | - | added 22 Nov; 92-120 m |
| [42273230](https://www.strava.com/segments/42273230) | Rund um Schwadorf | Brühl | 1.32 | 4 | 0.0 | 5 | - | added 22 Nov; 67-72 m |
| [30717355](https://www.strava.com/segments/30717355) | Brückensprint "SE neu" | Brühl | 0.31 | 6 | 2.4 | 8 | - | added 22 Nov; 62-70 m |
| [39665688](https://www.strava.com/segments/39665688) | Quinny's Bergsprint | Brühl | 0.51 | 9 | 1.5 | 9 | - | added 22 Nov; 62-70 m |
| [35060694](https://www.strava.com/segments/35060694) | Weiherhofsprint | Brühl | 0.97 | 0 | -0.1 | 2 | - | added 22 Nov; 64-66 m |

## Effort archive (tracked efforts, newest first)

### Mount Phantasialand (23234747), 1.56 km, 55 m, 3.5 %
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-27 15:49 | 3:41 | 1 | 25.6 | 248 | 4.43 | 100 | 97% | 88 | 182/189 |  |
| 2026-08-29 19:30 | 4:03 | 3 | 23.2 | 219 | 3.91 | 88 | 86% | 87 | -/- |  |
| 2026-08-19 15:44 | 3:45 | 2 | 25.1 | - | - | - | - | - | -/- |  |
| 2026-08-09 19:29 | 4:10 | 4 | 22.6 | - | - | - | - | - | -/- |  |
2 more effort(s) below the tracking threshold not listed.

### VochemBerg III (38595955), 0.56 km, 27 m, 4.9 %
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-27 16:41 | 1:25 | 1 | 23.6 | 277 | 4.94 | 100 | 89% | 84 | 178/187 |  |

### Raus aus der Stadt (41002017), 1.16 km, 2 m, -0.4 %
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-27 18:10 | 1:55 | 1 | 36.5 | 246 | 4.40 | 100 | 87% | 91 | 174/182 |  |
6 more effort(s) below the tracking threshold not listed.

### Theodor-Heuss Downforce (13203814), 1.27 km, 0 m, -2.4 %
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-27 17:48 | 1:43 | 1 | 44.5 | 255 | 4.56 | 100 | 87% | 96 | 179/184 |  |
| 2026-09-22 17:14 | 1:48 | 3 | 42.1 | 229 | 4.09 | 90 | 79% | 93 | 175/180 | stop 18s |
| 2026-08-30 18:54 | 1:46 | 2 | 43.3 | 209 | 3.72 | 82 | 72% | 100 | -/- |  |
16 more effort(s) below the tracking threshold not listed.

### Fischenich Ahoi (30701495), 1.58 km, 61 m, 3.5 % - no power or HR yet
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-11 17:44 | 4:42 | 1 | 19.8 | - | - | - | - | - | -/- |  |

### Kurfürsten Sprint (14456798), 0.48 km, 0 m, -1.3 % - segment min/max elevation implausible (Pat)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-27 17:07 | 0:43 | 1 | 40.5 | 305 | 5.45 | 100 | 77% | 96 | 169/177 |  |
| 2026-08-12 12:55 | 0:44 | 2 | 40.0 | - | - | - | - | - | -/- |  |
2 more effort(s) below the tracking threshold not listed.

### Flammgasse Climb (6678444), 0.57 km, 57 m, 9.8 %
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-27 16:04 | 2:16 | 1 | 14.9 | 270 | 4.82 | 100 | 99% | 79 | 184/189 |  |
1 more effort(s) below the tracking threshold not listed.

### Kierberger Sprint (42273304), 0.74 km, 4 m, -0.2 %
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-17 18:24 | 1:14 | 3 | 36.1 | 277 | 4.95 | 102 | 85% | 98 | -/- | HR data inaccurate and not usable (Pat: 17 Oct, derailleur failure ride) |
| 2026-10-02 16:28 | 1:22 | 5 | 32.9 | 236 | 4.22 | 87 | 75% | 84 | 171/182 |  |
| 2026-09-29 19:28 | 1:10 | 2 | 38.4 | 301 | 5.38 | 111 | 91% | 95 | 178/191 |  |
| 2026-09-27 18:48 | 1:09 | 1 | 38.9 | 270 | 4.83 | 100 | 81% | 93 | 173/180 |  |
9 more effort(s) below the tracking threshold not listed.

### Mühlenbach Climb (27969520), 0.77 km, 33 m, 4.2 % - not nearly all out (Pat)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-17 17:43 | 2:27 | 1 | 19.0 | 192 | 3.42 | 100 | 71% | 83 | -/- | HR data inaccurate and not usable (Pat: 17 Oct, derailleur failure ride) |
| 2026-08-07 16:18 | 2:35 | 2 | 18.0 | - | - | - | - | - | -/- |  |
1 more effort(s) below the tracking threshold not listed.

### Die UtkDoe Challenge (8001608), 0.94 km, 0 m, -0.9 %
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-08 18:04 | 1:16 | 1 | 44.2 | 283 | 5.05 | 100 | 88% | 94 | 175/182 |  |
| 2026-10-08 17:49 | 1:18 | 2 | 43.0 | 253 | 4.52 | 90 | 80% | 93 | 155/178 |  |
| 2026-09-30 18:15 | 1:25 | 3 | 39.2 | 253 | 4.51 | 89 | 81% | 93 | 179/185 |  |
| 2026-09-15 16:31 | 1:34 | 5 | 35.9 | 231 | 4.12 | 82 | 76% | 87 | 173/181 |  |
5 more effort(s) below the tracking threshold not listed.

### Ab auf den Müll! (10822662), 1.79 km, 2 m, -0.5 % - not all out (Pat)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-02 16:07 | 3:19 | 3 | 32.6 | 192 | 3.43 | 103 | 75% | 88 | 169/177 |  |
| 2026-09-22 16:59 | 3:15 | 1 | 33.3 | 186 | 3.32 | 100 | 72% | 85 | 162/169 |  |
| 2026-09-17 17:09 | 3:23 | 5 | 32.0 | 194 | 3.47 | 105 | 76% | 83 | 161/178 |  |
| 2026-09-17 17:00 | 3:16 | 2 | 33.0 | 211 | 3.76 | 113 | 82% | 86 | 167/179 |  |
| 2026-09-17 16:49 | 3:19 | 3 | 32.5 | 203 | 3.62 | 109 | 79% | 85 | 160/178 |  |
8 more effort(s) below the tracking threshold not listed.

### Long and windy road - Formtest (17867626), 7.87 km, 39 m, 0.5 %
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-01 14:52 | 15:55 | 1 | 29.7 | 182 | 3.24 | 100 | 97% | 86 | 172/178 |  |
1 more effort(s) below the tracking threshold not listed.

### Otto-Wels-Sprint (13164514), 1.70 km, 6 m, -0.6 % - PR on the very first road ride (Pat)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-10 19:50 | 3:13 | 2 | 31.3 | 207 | 3.69 | - | 80% | 84 | 167/173 |  |
| 2026-08-07 16:01 | 3:12 | 1 | 31.4 | - | - | - | - | - | -/- |  |
2 more effort(s) below the tracking threshold not listed.

### Liblarer->Bleibtreu See (8327378), 1.90 km, 17 m, 0.9 % - mostly easy drive-throughs, never all out (Pat)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-02 16:17 | 3:53 | 1 | 29.4 | 202 | 3.61 | 100 | 80% | 88 | 171/175 |  |
| 2026-09-22 17:08 | 4:09 | 5 | 27.5 | 187 | 3.34 | 93 | 74% | 82 | 166/169 |  |
| 2026-09-12 17:31 | 3:59 | 3 | 28.6 | 182 | 3.24 | 90 | 72% | 82 | 169/178 |  |
| 2026-09-05 20:00 | 4:00 | 4 | 28.6 | 180 | 3.21 | 89 | 71% | 76 | 166/169 |  |
| 2026-09-05 19:34 | 3:58 | 2 | 28.7 | 180 | 3.21 | 89 | 71% | 76 | -/- | HR unusable: 5 Sep min 20-36 (HR 75-130 at about 180 W, found 8 Nov) |
12 more effort(s) below the tracking threshold not listed.

### Fischenich Berg Gleise -> Ampel (21410880), 0.85 km, 42 m, 4.9 % - PR HR unusable (17 Oct); Pat: ~173 avg / ~182 max, not trustworthy
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-17 18:04 | 2:23 | 1 | 20.8 | 261 | 4.65 | 100 | 97% | 87 | -/- | HR data inaccurate and not usable (Pat: 17 Oct, derailleur failure ride) |
| 2026-09-10 19:01 | 2:38 | 2 | 18.9 | 223 | 3.97 | 85 | 84% | 68 | -/- | HR unusable: strap gaps and dropouts 10 Sep min 13-58 (km about 5-22; Pat's screenshot: frozen line km 7.3-13.5 = missing data, drop to 0 at km 13.6) |

### Fischenich Berg (979311), 1.05 km, 51 m, 4.9 % - Strava low/high elevation 21-72 m is offset by about -54 m (Edge 75-125 m; Gleise -> Ampel on the same climb matches the Edge within 2 m); the 51 m difference is right. PR HR unusable (17 Oct)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-17 18:04 | 2:55 | 1 | 21.6 | 257 | 4.59 | 100 | 98% | 88 | -/- | HR data inaccurate and not usable (Pat: 17 Oct, derailleur failure ride) |
| 2026-09-10 19:01 | 3:20 | 2 | 19.0 | 216 | 3.85 | 84 | 84% | 71 | -/- | HR unusable: strap gaps and dropouts 10 Sep min 13-58 (km about 5-22; Pat's screenshot: frozen line km 7.3-13.5 = missing data, drop to 0 at km 13.6) |

### Metternich Climb (28467890), 0.35 km, 29 m, 8.2 % - not all out (Pat 22 Nov); felt slightly steeper than 8.2% (Pat)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-22 16:30 | 1:34 | 1 | 13.9 | 236 | 4.21 | 100 | 78% | 99 | 165/177 |  |

### Mur von Metternich (3171185), 0.60 km, 27 m, 4.5 % - not all out (Pat 22 Nov); contains Metternich Climb (Pat: the 'pre' and 'post' parts)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-22 16:30 | 2:22 | 1 | 15.7 | 191 | 3.41 | 100 | 71% | 93 | 164/177 |  |

### Zum Swister Turm (7715142), 0.47 km, 23 m, 5.0 % - not all out (Pat 22 Nov)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-20 16:20 | 1:34 | 2 | 17.9 | 221 | 3.95 | 97 | 73% | 81 | 167/170 |  |
| 2026-09-08 17:43 | 1:27 | 1 | 19.3 | 228 | 4.08 | 100 | 74% | 76 | 177/187 |  |
| 2026-08-20 19:57 | 1:41 | 3 | 16.6 | - | - | - | - | - | -/- |  |
2 more effort(s) below the tracking threshold not listed.

### RM Phanta go (17971906), 0.92 km, 42 m, 4.5 % - PR without power or HR (19 Aug); not all out (Pat 22 Nov)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-29 18:34 | 2:41 | 5 | 20.6 | 209 | 3.73 | 82 | 79% | 78 | 174/179 |  |
| 2026-09-27 15:50 | 2:19 | 1 | 24.0 | 255 | 4.55 | 100 | 94% | 87 | 187/189 |  |
| 2026-08-29 19:32 | 2:27 | 3 | 22.6 | 244 | 4.36 | 95 | 90% | 88 | -/- |  |
| 2026-08-19 15:45 | 2:20 | 2 | 23.8 | - | - | - | - | - | -/- |  |
| 2026-08-09 19:31 | 2:35 | 4 | 21.6 | - | - | - | - | - | -/- |  |
1 more effort(s) below the tracking threshold not listed.

### Kurfürsten Sprint lang (31536033), 0.82 km, 0 m, -0.7 % - PR without power or HR (12 Aug); Strava gain 0 is not quite right: a dip and rise at a railway bridge (Pat)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-12 12:55 | 1:23 | 1 | 35.7 | - | - | - | - | - | -/- |  |
3 more effort(s) below the tracking threshold not listed.

### Eisenwerk Brühl (40613488), 0.55 km, 0 m, 0.0 % - PR without power or HR (17 Aug)
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-08-17 18:51 | 1:07 | 1 | 29.6 | - | - | - | - | - | -/- |  |

### No10 revers (35140485), 0.63 km, 0 m, 0.0 % - Langenackerstraße, Brühl-Ost (Pat 22 Nov); first attempt on 22 Nov, about 5 min into the ride (cold); [mine] the 75 s, 263 W connector effort
| Date | Time | Rank | km/h | W | W/kg | % of PR W | % of ability | Cad | HR avg/max | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-22 13:02 | 1:15 | 1 | 31.8 | 264 | 4.71 | 100 | 81% | 99 | 177/183 |  |

### Attempted, no tracked effort yet (every effort below the threshold, or counted only)
| Segment | Efforts | Best effort | W | % of ability | Note |
|---|---|---|---|---|---|
| Such dir ein schnelles Hinterrad! (13395002) | 3 | 2026-10-30 15:12 (1:18) | 194 | 61% | not all out (Pat 22 Nov) |
| Erp-Friesheim (7228295) | 3 | 2026-11-21 15:53 (5:03) | 156 | 63% | not all out (Pat 22 Nov); PR on the 21 Nov ride (Pat wrote 22/11; the connector effort and the file match 21 Nov) |
| L33 ost (27440949) | 3 | 2026-09-20 14:52 (4:31) | 144 | 58% | not all out (Pat 22 Nov) |
| Knallgas runter (17985090) | 2 | 2026-11-21 16:37 (1:02) | 177 | 52% | descent; not all out (Pat 22 Nov); PR on the 21 Nov ride (Pat wrote 22/11) |
| Römersprint (18357516) | 9 | 2026-09-10 19:35 (1:08) | 206 | 62% | not all out (Pat 22 Nov); ridden on 21 Nov but not in that ride's Strava segment list (Pat) |
| Nörvenich 6k TT (32958179) | 1 | 2026-11-22 15:14 (13:14) | 135 | 70% | not all out (Pat 22 Nov); the 22 Nov long ride at Z2 |
| Nörvenich 5km TT (4462552) | 1 | 2026-11-22 15:10 (10:56) | 133 | 67% | not all out (Pat 22 Nov); inside the 6k TT |
| Swister Turm runter (10165958) | 2 | 2026-09-29 18:46 (1:24) | 205 | 65% | descent; not all out (Pat 22 Nov) |
| Sprint von A553 zur A61 (14573652) | 3 | 2026-09-20 16:14 (2:09) | 163 | 59% | not all out (Pat 22 Nov); Strava low/high elevation offset (32-42 m; the area is about 100 m) |
| Ortsschildsprint Brühl City (41393364) | 2 | 2026-09-27 16:16 (1:01) | 118 | 34% | not all out (Pat 22 Nov) |
| Mit Schwung in die Stadt (17478206) | 4 | 2026-08-30 18:58 (0:43) | 245 | 62% | not all out (Pat 22 Nov); no HR on the PR ride; Pat: the gain should be higher (a rise after the bridge) |
| Erdbeer-Radweg (9963429) | 1 | 2026-11-22 15:47 (6:14) | 58 | 26% | counted only (Pat) |

## Observations [mine]
- Closest to his ability (best tracked effort / capability curve): Flammgasse Climb 99% (2026-09-27, 270 W); Fischenich Berg 98% (2026-10-17, 257 W); Long and windy road - Formtest 97% (2026-11-01, 182 W); Mount Phantasialand 97% (2026-09-27, 248 W); Fischenich Berg Gleise -> Ampel 97% (2026-10-17, 261 W): the 27 Sep
  segment challenge, the 17 Oct climbs and the 1 Nov 4DP week; these PRs need a fresh, full effort to beat.
- Most room: Mur von Metternich 71%; Mühlenbach Climb 71%; Zum Swister Turm 74%; Kurfürsten Sprint 77%; Metternich Climb 78%; Liblarer->Bleibtreu See 80%; Otto-Wels-Sprint 80%; No10 revers 81%. A fresh full effort should beat these (No10 revers was
  ridden 5 min into a ride at about 3 C; Metternich Climb and Mur von Metternich came 3:30 h into the 22 Nov long ride).
- No tracked effort yet (12 segments, all PRs from easy riding): Such dir ein schnelles Hinterrad!, Erp-Friesheim, L33 ost, Knallgas runter, Römersprint, Nörvenich 6k TT, Nörvenich 5km TT, Swister Turm runter, Sprint von A553 zur A61, Ortsschildsprint Brühl City, Mit Schwung in die Stadt, Erdbeer-Radweg. Any real effort sets a tracked mark there.
- PR dates (the tool's fastest effort per segment): 2026-09-27 9, 2026-11-22 6, 2026-10-17 3, 2026-11-21 2, 2026-09-20 2, 2026-09-08 1.
- HR on segments: the highest strap HR in a segment effort is still 191 bpm (29 Sep, Kierberger Sprint, 75 s above 300 W: a smooth rise);
  his cycling max is set to 195 [Pat 12 Nov] (194 on the trainer on 11 Nov). 22 Nov: No10 revers 177 average, 183 at the end.
- Repeatable flat benchmarks: Long and windy road (7.87 km, 1 Nov PR 182 W = 97% of ability) and the Nörvenich 5 km / 6 km TTs (both so far
  only at Z2 pace, 133-135 W); all wind-dependent. The climbs (Mount Phantasialand, RM Phanta go, Flammgasse, Mühlenbach, the Fischenich and
  Metternich climbs) are the least wind-sensitive. Most ridden: Theodor-Heuss Downforce (19 efforts), Liblarer->Bleibtreu See (17), Ab auf den Müll!
  and Kierberger Sprint (13 each).
- On the plan routes, in riding direction: C27 century (29 Nov): Nörvenich 5 km / 6 km TT (km 78.7 / 80.3), Erdbeer-Radweg (89.6),
  Liblarer->Bleibtreu See (95.5), Theodor-Heuss Downforce (98.3), Kierberger Sprint (100.5); in reverse: Ortsschildsprint Brühl City, L33 ost,
  Erp-Friesheim. C30 v2 (22 Nov): Kurfürsten Sprint (lang) km 0.6, No10 revers 2.3, Mount Phantasialand 7.4, RM Phanta go 8.1, Swister Turm
  runter 12.8, the Nörvenich TTs 45.9 / 47.5, Erdbeer-Radweg 57.6, Sprint von A553 zur A61 64.8, Mur von Metternich / Metternich Climb 71.7,
  Knallgas runter 75.8, Ortsschildsprint Brühl City 81.5.
- The steepest to-do climbs reach 13.5-13.8% (Stationsweg Kreuzberg, Venusberg "Die Mauer"); Rampe nach Hemmerich and Wand von Merten probably
  have 100-200 m at 10-14% [tentative, quäldich / climbfinder]. With 34x34 as the lowest gear (2.10 m wheel, 68 kg) 13.8% means about 58 rpm at
  200 W, 72 rpm at 250 W and 86 rpm at 300 W: fine all out, a grind at easier power.

## Updating
1. New export in the repo -> update `segments.json` 'capability' if a best changed -> `python3 segments_tool.py` -> new `segments_archive.csv` (tracked efforts) and these tables; check the
   found counts against Strava.
2. New segment: Pat sends the link and Strava values (distance, gain, grade, low/high elevation, PR time, W, cadence, HR avg/max,
   efforts, category) -> `fingerprint()` locates the PR ride -> `add_segment()` -> commit `segments.json`. A to-do segment gets its
   reference line from the first ride over it (same fingerprint once Pat sends the PR values).
3. A PR on a segment without power/HR: also give the elevation difference; check the effort count.
4. Pat reports a ride with bad HR -> add it to `hr_unusable` in `segments.json` (whole ride, or a minute range); `cp.hr_artefact_scan` and
   `cp.hr_gaps` find candidates.
5. A segment to count but not list (Pat's choice, e.g. Erdbeer-Radweg): `"track": false` in its `segments.json` entry.
6. A PR effort that includes a stop (no fingerprint match): locate it from the connector's segment effort (elapsed and moving time,
   average power) in the ride file, then `add_segment()` with those samples (Erdbeer-Radweg, 22 Nov).
7. The tracking thresholds (`min_rel_power` 0.80, `min_cap_frac` 0.70, `min_ftp_frac` 0.90 with `ftp`, `max_listed` 10, `keep_worst` 2) live in
   `segments.json` 'tracking'; raise `ftp` with the planning FTP.

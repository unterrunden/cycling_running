# Routes and courses: Pat (cycling + running), status 11 Nov 2026

Purpose: one place where Claude finds every route Pat uses, sorted by purpose, so a route can be picked for a session. New routes are analysed with `routes_tool.py` (GitHub repo) and added with the template at the end.

Conventions:
- IDs are stable: C = cycling, U = running, S = Strava saved routes. Removed so far: the old 4DP v1 loop (komoot 3316196558), C5 (unchecked komoot suggestions) and C12 (near-duplicate of C8).
- Geometry is computed from the GPX: sharp turn = heading change of at least 55° within 100 m; ascent uses 60 m smoothing and a 2 m threshold, so komoot's own figures differ; "wind" names the effect of the two usual wind directions on the longest straight (reversed direction flips it).
- [Pat] He checks every route himself before using it for efforts. Roads are assumed paved unless he says otherwise; surface, crossing and traffic-light notes are only recorded when he mentions them, komoot alerts only when he flags them.
- Wind in the area: usually from the south, second most common from the west.
- GPX formats [Pat, 7 Nov]: komoot's own export works only for routes inside his unlocked area (Rhein-Erft-Kreis); routes starting outside it are exported with a third-party tool, which writes route points (`<rtept>`, creator "komootGPXport") instead of track points. `routes_tool.py` reads both.
- Daylight (Cologne, computed): sunset 17:02 on 5 Nov, 16:47 on 15 Nov, 16:32 on 29 Nov, 16:26 on 13 Dec (the earliest); civil dusk about 35-40 min later. Weekday outdoor sessions after about 16:00 need lights and quiet roads; steady efforts belong on the trainer.

## How to pick a route (selection guide)
| Session | Routes | What the route must offer |
|---|---|---|
| Z2 endurance ride (60-75 km at weekends) | C10, C11, C14, C15, C17; shorter: C8, C9, C24; Strava S routes | Flat to rolling, few stops, climbs under about 5% |
| First 100 km | C27 (century, Pat's plan); alternatives C25 (flatter), C16 (hillier) | Mostly flat, fuel and water stops, home before dusk |
| Steady state 10-30 min | C28 (km 21.5-32.9 S stretch and the following legs), C21 / C22 (17.7-18 km straight), C1 south stretch (10.7 km), C2 (11.7 km), C23 (10.2 and 9.5 km legs), C19, C17 (21 km), C14 (15.7 km), C10 (12.6 km) | 10+ km with at most 1-2 gentle direction changes and no traffic lights; constant slope is a plus |
| 60-min test outdoors | C28 from about km 17 (ends about km 47-48) | 30-31 km with few turns, wind roughly cancelling |
| 20-min test outdoors (the trainer is preferred) | C2 or C21 in any wind; the C1 south stretch in calm air or a headwind | About 9.5-12 km without interruptions (8 km into a 10 km/h headwind, 12 km with a 10 km/h tailwind) |
| 4DP | C1 | Straights for the sprints, 5 min and 20 min, about 1 km for the final minute, the big chainring |
| Short hard intervals (1-3 min) | C7 (Hessenweg) | Quiet, straight, both directions usable |
| Climbs / torque | C6 segments; C26 for longer climbs | Steep ones (9-14%) need low gearing: 34x34 is the lowest |
| Easy run | U1, U2, U3, U4 (roads are fine too) | No large intersections, traffic lights or other interruptions, no long steep climbs |
| Hard run / 5K | U1 (Schlosspark) | Flat, no stops, loop or out-and-back with a gentle turn |

## CYCLING

### Tests and steady state

### C1: 4DP loop ("4dp v2", komoot tour 3373226373; version ridden on 1 Nov)
- Type: loop from home, 55.1 km, +166/-168 m, steepest 500 m +5.2%, highest point 153 m; closes within 32 m. (The 31 Oct draft was 56.9 km; the 1 Nov version shortens the Kerpen section.)
- Geometry (km: what; 28 sharp turns, 0.51/km):
  - 0-9.2: 4 corners at km 2.0-2.7, then 6.5 km WSW (240°): warm-up
  - 9.2-13.2: corner cluster (km 9.2, 9.9, 11.7 and six turns within km 12.4-13.2)
  - 13.2-15.7: 2.5 km NW (309°), the sprints; 15.9-19.6: 3.7 km NW (313°), the 5 min, roundabout at about km 18.7 [Pat]
  - 19.6 (-84°) and 20.8 (-88°) into the south stretch
  - 20.8-31.5: 10.7 km S (172°, +0.5%) with moderate bends at km 23.0/23.2 (48°/36°), a state-road intersection at about km 24.8 [Pat] and roundabouts later on [Pat]; this stretch runs on C2's south section (C2 km 0.8-11.6)
  - 31.5 (-93°, leaving the state road), 1.3 km E (84°); 32.9 (-95°), 33.3 (+112°); 33.3-37.2: 3.9 km ESE; six turns within km 37.2-38.2; 38.2-42.6: 4.5 km ESE
  - 42.6 (-68°), then 12.0 km NNE (23°, -0.4%) home; last corner at km 54.6
- Effort positions on 1 Nov (ride GPS matched to the route): sprints km 13.5-13.7 (from a standstill) and 14.0-14.1 (rolling); 5 min km 16.1-18.65 (ended at the roundabout); strap stop at km 20.8 (3:14); compensation bout km 20.9-22.6; 20 min km 22.7-32.7 (10.0 km); 1 min on km 31.6-32.2 eastbound after a short out-and-back in the recovery, which made the ride 2.6 km longer (57.7 km).
- Issues and fixes [Pat, after the 1 Nov test]:
  1. The 5 min ended right at the roundabout (about km 18.7) with cars approaching, so no finishing kick: start the 5 min slightly earlier (fine unless wind or power change a lot).
  2. The state-road intersection at about km 24.8 inside the 20 min is risky to cross at full speed: visible from both sides and fine with little traffic, but it needs attention. Roundabouts later in the block can slow him down if cars are in them (happened once).
  3. He was faster than expected and the wind was lighter, so the end of the 20 min ran into sections meant for recovery and not suited to the test (after leaving the state road at km 31.5). Possible fix: start the 20 min at the beginning of "Vinger Weg" as in the 31 Oct routing.
  - [Pat, 6 Nov] Decision: the route stays as ridden on 1 Nov (komoot 3373226373, unchanged); the issues came mostly from the strap stop, not the route. Keep issues 1-2 in mind (start the 5 min a little earlier; care at the km 24.8 intersection).
  - [mine] On 1 Nov the strap stop and compensation bout used the first 1.9 km of the straight. Started at about km 20.9, a 10 km block would have ended about km 30.9, before the exit.
- Wind (south stretch, 172°): south wind = headwind, west wind = crosswind, north wind = tailwind. 20 min at 185 W covers about 9.9 km in calm air, about 8.0 km with a 10 km/h headwind and about 11.9 km with a 10 km/h tailwind (my model: 72 kg, CdA 0.38, +0.4%). On 1 Nov: 10.0 km at 183 W in near-calm air (Strava weather NE 4 km/h).
- Status: 4DP ridden Sun 1 Nov 2026 (results in coach_notes.md); the Sat 31 Oct mock ride used most of the loop. [Pat, 6 Nov] Final 4DP ideally Sun 20 Dec, outdoors on C1 if the weather allows (direct comparison), otherwise on the trainer; tests indoors after that.

### C28: "ftp" v2 (komoot tour 3386583719, 8 Nov; route export via the third-party tool)
- Type: loop from home, 62.5 km, +142/-144 m, steepest 500 m about +3.3% / -3.3%, 82-139 m; closes at home.
- [Pat] Built from solid sections already ridden for an outdoor 60-min FTP test: start at about km 17, end anywhere before km 47 to about 50 depending on wind and form. (The first version of 8 Nov, 48.8 km, was too short: its loop from km 12.8 closed after 23.3 km.)
- Geometry (29 sharp turns, 0.46/km): km 2.7-9.2 6.5 km WSW (240°); corner cluster km 9.9-13.2 (eight turns); 13.2-15.7 2.5 km NW; 15.9-20.3 4.4 km NW (317°); test part from km 17: four turns at km 20.3 (-105°), 20.8 (+90°), 20.9 (-58°), 21.5 (-76°); 21.5-32.9 11.5 km S (172°, +0.5%) = the C1/C2 state-road stretch (bends at km 24.2/24.4, the intersection Pat flagged on 1 Nov at km 26.0); +94° at 32.9; 32.9-36.5 3.5 km W (262°); +82° at 36.5; 36.5-42.5 6.1 km N (358°, -0.3%); +86° at 42.5; 42.5-50.9 8.4 km E (96°, -0.3%); then -82°/+58° at 50.9/51.1, 2.2 km NE, +84° at 53.3, 6.5 km ENE (60°) and the last corners near home (km 59.8-60.5).
- [mine] Length check: 60 min at 170-190 W (Stages) covers about 30-31 km in calm air (model 72 kg, CdA 0.38; on 1 Nov 10.0 km in 20 min at 183 W), so from km 17 the hour ends about km 47-48 on the E leg, with 3 km of buffer to the turn at km 50.9. Inside the hour: 7 sharp turns, four of them in the first 4.5 km (km 20.3-21.5, while still fresh), then three 90° corners about 11, 15 and 21 km in. Net +22 m from km 17 to 47 (barely noticeable).
- Wind: the legs nearly cancel (S 11.5 km, W 3.5 km, N 6.1 km, E 5-8 km): south wind = headwind on the long S leg and tailwind on the N leg; west wind = headwind on the W leg, tailwind on the E leg (the finish).
- Status: new on 8 Nov 2026, not ridden as a whole yet; the 60-min test is indoors in week 1 once the new fan is there, this is the outdoor option (a Sunday, for daylight and traffic). Sunset on Sunday 15 Nov 16:47 and 22 Nov 16:38 (Cologne, computed): start the test by about 14:00.

### C2: "15km uninterrupted" (komoot tour 3335957752)
- Type: point-to-point, 15.0 km, +58 m; start near Langenich (50.867 N, 6.682 E, about 16 km from home), end near Gladbach (50.762 N, 6.659 E). Ride out, test, ride back.
- Geometry: south for 11.7 km (161-194°) at +0.2-0.7% (83 to 133 m); soft -48° at km 3.1; sharp +97° at km 11.7; then 3.3 km west.
- [Pat] Paved throughout. Open fields, no wind shelter. Km 0.8-11.6 is the same road as the C1 south stretch; he rode about 8 km of it in the 1 Nov 4DP.
- Good for: 20-min test and steady-state blocks in any wind (the effort ends before km 11.7 unless there is a strong northerly tailwind).

### C3: "15km uninterrupted 2" (komoot tour 3335967084)
- Type: point-to-point, 15.0 km, +59 m; start near Brüggen/Gymnich (50.855 N, 6.731 E).
- Geometry: south with six direction changes (+49° km 0.3, -39° km 1.4, +38° km 3.6, +84° km 8.6, -84° km 10.3, +89° km 11.8); longest stretch 4.9 km (km 3.6-8.6).
- Good for: 20-min test in a headwind or calm only; a tailwind would carry him through the sharp bends.

### C21: "20km uninterrupted" (komoot tour 3379318400)
- Type: point-to-point, 20.0 km, +44/-21 m, steepest 500 m +2.0%; start 50.8115 N, 6.5598 E (23.8 km west of home), end 50.6882 N, 6.7405 E.
- Geometry: 2 sharp turns (km 0.3, -67°; km 2.4, -56°), then 17.7 km straight SE (133°, +0.1%, km 2.4-20.0).
- Wind (133°): south wind = quartering headwind, west wind = tailwind. It is identical to the first 20 km of C22.
- Good for: 17.7 km without a sharp turn (only C17's 21 km straight is longer): a 20-min test in any wind (17.7 km covers even a strong tailwind) and steady state up to about 35 min. The start is about 24 km from home, which serves as the warm-up.
- Status: new on 5 Nov 2026, not ridden yet.

### C22: "30km uninterrupted" (komoot tour 3379328216)
- Type: point-to-point, 30.0 km, +47/-62 m, steepest 500 m +2.0%; same start as C21, end 50.7588 N, 6.7951 E (about 12 km from home, near the start of C23).
- Geometry: km 0-20.3 as C21 (18.0 km SE straight), then +105° at km 20.3 and 9.7 km NNE (26°, -0.5%) to the end.
- Wind: SE leg as C21; NNE leg: south wind = tailwind, west wind = crosswind.
- Good for: two long steady-state blocks; ends on the way home.
- Status: new on 5 Nov 2026, not ridden yet.

### C19: "uninterrupted loop (16km)" (komoot tour 3372490972; file of 9 Nov: loop only, route export via the third-party tool)
- Type: loop, 16.5 km, +23/-22 m (flat, 119-139 m, steepest 500 m +0.8%), closes within 19 m; start and end at 50.8027 N, 6.6870 E (15.3 km straight line from home), just before the corner between the ESE and SSE legs. [Pat, 9 Nov] The file now holds only the loop (the earlier komoot export, limited to start and end inside the Rhein-Erft-Kreis, included a 5.3 km approach from 50.8005 N, 6.7627 E).
- Geometry: 4 corners (km 0.1 +58° where the file starts just before the corner, 4.5 +96°, 8.0 +82°, 14.1 +80°); legs: 4.4 km SSE (164°, +0.4%), 3.5 km W (262°), 6.1 km N (358°, -0.3%), 2.5 km ESE (105°, -0.1%); no other bends of 35° or more.
- Wind: N leg: south = tailwind, west = crosswind; SSE leg: south = headwind; W leg: west = headwind; ESE leg: west = tailwind.
- Good for: steady state or a 20-min effort (9.5-10 km in calm air at 185 W = two legs and two corners); laps for longer blocks (one lap about 32-33 min at 30 km/h); about 15 km from home each way.
- Status: not ridden yet.

### C4: Berrenrather Börde test loops 1-3 (komoot planner: loop 1 = 3335949710, loop 2 = 3335951013, loop 3 = 3319717819)
- Three small loops near Knapsack/Brüggen (start about 50.861 N, 6.782 E, 8.1 km from home), each with four corners of about 76-95°.
  - Loop 1: 3.9 km, +10 m, 1.02 corners/km, longest straight about 1.2 km; on a cycleway parallel to the K50 without direct traffic contact.
  - Loop 2: 3.6 km, +4 m, 1.11 corners/km, longest straight about 1.0 km.
  - Loop 3: 6.0 km, +13 m, 0.67 corners/km, longest straight about 2.1 km (2.1 km N, 1.2 km S/SSE legs). [Pat] It crosses the K50 twice in each direction; the crossings are easy to see but can cause short delays when cars pass.
- A 20-min effort covers about 9.5-10 km: roughly 6-7 corners on loop 3 versus about 10 on loop 1 (about 10 corners cost an estimated 2-3% of average power). Loop 3 is the best of the three.
- [Pat] The ride out can serve as a warm-up or for steady-state work.

### Endurance loops from home (by length)

### C20: house loop to Hürth and back via the state road (strava_10km_house_loop.gpx)
- Type: loop from home, 10.0 km, +81/-82 m, 9 sharp turns; longest straights 2.1 km N (359°), 2.1 km WSW (248°), 1.9 km SSW (193°). [Pat] A very small cycling route (also runnable).
- The same route as Strava saved route S12 "Threshold Sprint 10km" (about 90% overlap).
- Good for: a short recovery spin or a quick opener ride.

### C9: Road cycling 27km (komoot tour 3267868308)
- Type: loop from home, 27.4 km, +111/-116 m, steepest 500 m +4.9%, highest point 153 m.
- Geometry: 10 sharp turns (0.36/km); longest straights 10.3 km NNE (23°, -0.4%, from km 16.7), 6.3 km SW (231°, from km 2.8), 4.6 km SE (130°, from km 11.1).
- Wind (10.3 km straight): south = tailwind, west = quartering tailwind.
- Good for: a short loop with a 10 km straight for a steady block.
- Status: [Pat] ridden once.

### C8: Road ride 44km (komoot tour 3213993327)
- Type: loop, 44.3 km, +176/-175 m, steepest 500 m +3.5%, highest point 136 m; start 0.7 km from home (50.8384 N, 6.8885 E).
- Geometry: 33 sharp turns (0.75/km); longest straights 5.0 km NE (54°, from km 36.6), 4.3 km NNE (from km 2.1, -0.8%), 4.1 km SSE (from km 32.5).
- Wind (5.0 km straight): south = quartering tailwind, west = tailwind.
- Good for: easy or moderate rides from the door; many corners, not for steady state.
- Status: [Pat] ridden twice on a route that follows it closely.

### C15: Road cycling 50km (komoot tour 3216293914)
- Type: loop from home, 50.0 km, +178/-178 m, steepest 500 m +7.2%, highest point 160 m.
- Geometry: 18 sharp turns (0.36/km); longest straights 12.2 km NNE (22°, -0.4%, from km 36.4), 11.9 km NW (318°, from km 24.4), 5.8 km SSE (from km 2.6).
- Wind (12.2 km straight): south = tailwind, west = quartering tailwind.
- Good for: endurance ride with two 12 km straights for steady blocks.
- Status: [Pat] ridden once, soon after he got the road bike.

### C11: Road cycling 60km (komoot tour 3280455509)
- Type: loop from home, 60.3 km, +184/-186 m, steepest 500 m +7.3%, highest point 159 m.
- Geometry: 17 sharp turns (0.28/km); longest straights 11.6 km NNW (331°, from km 24.8), 8.8 km SSE (163°, from km 0.5), 7.7 km WNW (291°, from km 36.4).
- Wind (11.6 km straight): south = tailwind, west = quartering headwind.
- Good for: endurance ride with 8-12 km straights and one short steeper climb.
- Status: not ridden yet.

### C14: Road ride 60km, second 60 km route (komoot tour 3213949240)
- Type: loop from home, 60.0 km, +186/-197 m, steepest 500 m +7.2%, highest point 167 m.
- Geometry: 15 sharp turns (0.25/km); longest straights 15.7 km NW (323°, -0.2%, from km 41.5), 11.4 km SSW (210°, +0.6%, from km 7.6), 9.4 km NNE (17°, from km 32.0).
- Wind (15.7 km straight): south = tailwind, west = quartering headwind.
- Good for: endurance ride; the 15.7 km NW leg suits a steady block with a southerly wind at the back.
- Status: not ridden yet.

### C10: Speedy loop (62km) (komoot tour 3268834956)
- Type: loop from home, 62.0 km, +184/-195 m, steepest 500 m +4.9%, highest point 153 m.
- Geometry: 22 sharp turns (0.35/km); longest straights 12.6 km SE (131°, +0.2%, from km 16.8), 10.9 km NNE (24°, -0.4%, from km 50.6), 9.5 km N (353°, from km 37.8).
- Wind (12.6 km straight): south = quartering headwind, west = tailwind.
- [Pat] Few crossings in the loop section. C23 lies entirely on this route.
- Good for: endurance ride with three 9-13 km straights for 10-20 min steady blocks.
- Status: [Pat] ridden once.

### C17: Road cycling 73km (komoot tour 3262741021)
- Type: loop from home, 73.7 km, +247/-251 m, steepest 500 m +7.1%, highest point 174 m.
- Geometry: 35 sharp turns (0.47/km); longest straights 21.1 km SW (218°, +0.5%, km 11.9-33.1), 7.0 km NNW (from km 37.8), 4.4 km N (from km 46.0).
- Wind (21.1 km straight): south = headwind, west = quartering headwind; the way back is downwind.
- Good for: a long steady state or a 20-min test on the 21 km straight.
- Status: not ridden yet.

### C27: century (komoot tour 3379567079), Pat's plan for the first 100 km ride
- Type: loop from home, 101.4 km, +312/-312 m, steepest 500 m +6.3%, highest point 195 m; furthest point 30.3 km west of home (route km 59.3, about 50.752 N, 6.488 E).
- Geometry: 39 sharp turns (0.38/km); longest straights 11.4 km WNW (294°, km 18.9-30.2), 9.0 km ENE (76°, km 77.4-86.4), 7.9 km N (351°, km 57.5-65.4). Climbs of 3% or more over 500 m: km 11.3 (1.3 km, +45 m), km 12.6 (0.9 km, +22 m), km 53.3 (0.9 km, +24 m); otherwise flat.
- Wind: west = headwind on the way out (WNW leg) and tailwind on the way back (ENE leg); [mine] that is the better order, with the headwind early and fresh.
- [Pat] The current plan for the first 100 km ride; he may adjust it slightly. [Pat, 6 Nov] Planned for Sun 29 Nov (all weekends possible, Sundays preferred); sunset 16:32 on 29 Nov.
- Status: new on 5 Nov 2026, not ridden yet.

### C25: 100km 3 (komoot tour 3379365619)
- Type: loop from home, 100.4 km, +268/-269 m, steepest 500 m +4.2%, highest point 164 m; furthest point 25.3 km from home (route km 56.7).
- Geometry: 39 sharp turns (0.39/km); longest straights 10.2 km SSW (204°, +0.4%, km 0.5-10.7), 9.4 km ESE (103°, km 74.1-83.5), 7.5 km NNW (342°, km 51.4-58.9). Only climb of 3% or more: km 4.2 (1.6 km, +45 m).
- Wind (10.2 km straight): south = headwind, west = quartering headwind.
- Good for: a flatter 100 km alternative to C27.
- Status: new on 5 Nov 2026, not ridden yet.

### C16: Road cycling 100km 2 (komoot tour 3257037426)
- Type: loop from home, 100.3 km, +595/-596 m, steepest 500 m +7.3%, highest point 415 m.
- Geometry: 52 sharp turns (0.52/km); longest straights 12.0 km NNE (21°, from km 75.9), 11.0 km NNE (23°, from km 87.9), 6.5 km SSE (from km 2.5).
- Wind (12.0 km straight): south = tailwind, west = quartering tailwind.
- Good for: a reference for a hilly 100 km.
- Status: not ridden yet.

### C26: 111km (komoot tour 3379483490)
- Type: loop from home, 111.0 km, about +930-950 m (a 59 m elevation spike in the komoot data at km 65.8; with a median filter +927 m), steepest 500 m +9.9%, highest point 512 m; furthest point 40.9 km from home (route km 57.7, about 50.615 N, 6.439 E).
- Geometry: 68 sharp turns (0.61/km); longest straights 18.5 km WSW (243°, +0.9%, km 20.1-38.6), 10.9 km NNE (24°, km 99.6-110.5), 8.3 km NNE (km 83.9-92.2). Main climbs: km 40.5 (2.4 km, +108 m), km 43.5 (1.6 km, +68 m), km 45.6 (1.7 km, +73 m), km 53.9 (4.3 km, +226 m).
- Wind (18.5 km straight): south = quartering headwind, west = headwind on the way out; downwind home.
- Good for: a long hilly ride with real climbs. [mine] Better after the first 100 km than before it.
- Status: new on 5 Nov 2026, not ridden yet.

### C18: Road ride 150km (komoot tour 3214003257)
- Type: loop from home, 150.1 km, +847/-852 m, steepest 500 m +9.7%, highest point 511 m (some elevation spikes in the komoot data).
- Geometry: 66 sharp turns (0.44/km); longest straights 12.2 km ESE (from km 126.3), 10.1 km NNE (from km 139.5), 9.7 km SSW (from km 22.9).
- Good for: a reference for a very long ride (not planned).
- Status: not ridden yet.

### Loops away from home

### C23: 30km loop (komoot tour 3379330088)
- Type: loop, 29.6 km, +52/-51 m, steepest 500 m +2.2%; start 50.7538 N, 6.8076 E (11.7 km from home); furthest point 16.3 km from home.
- Geometry: 8 sharp turns (0.27/km; turnarounds of -179° at km 1.1 and -148° at km 29.2); longest straights 10.2 km ESE (119°, km 1.1-11.3), 9.5 km N (353°, -0.2%, km 19.7-29.2), 4.0 km WNW (km 14.9-18.9), 3.7 km WSW (km 11.3-14.9).
- Wind: ESE leg: south = quartering headwind, west = tailwind; N leg: south = tailwind, west = crosswind.
- It lies entirely on C10 and about 93% on C24. The 11.7 km there serve as the warm-up.
- Good for: two 10 km steady-state legs.
- Status: new on 5 Nov 2026, not ridden yet.

### C24: 50km loop (komoot tour 3379348878)
- Type: loop, 49.5 km, +94/-95 m, steepest 500 m +2.2% (no climb of 3% or more); start 50.7482 N, 6.8380 E (11.3 km from home); furthest point 21.7 km from home.
- Geometry: 15 sharp turns (0.30/km); longest straights 8.4 km ESE (105°, km 41.1-49.5), 7.6 km ENE (78°, km 32.2-39.8), 6.8 km ESE (123°, km 0.0-6.8), 5.0 km NW (km 15.2-20.2).
- Wind (8.4 km straight): south = crosswind, west = tailwind.
- Good for: a flat endurance loop (about 72 km with the ride there and back).
- Status: new on 5 Nov 2026, not ridden yet.

### Intervals and segments

### C7: Anaerobic 1-3 minute Power Intervals (komoot tour 3252126507)
- Type: loop from home, 23.3 km, +58/-62 m, steepest 500 m +2.9%; 22 sharp turns (0.95/km); longest straights 3.0 km ENE (64°, km 8.4-11.4), 2.9 km W (267°, from km 16.7), 2.4 km NW (308°, from km 20.4).
- [Pat] The 1-3 min intervals of the 4-week sprint plan (31 Aug-27 Sep) were done on the Hessenweg between Walberberg and Keldenich: quiet and straight, used in both directions; the usual wind (from the Walberberg side) is a tailwind towards Keldenich. Used about 5 times during that plan, never before it. [mine] The 3.0 km ENE stretch at km 8.4-11.4 (50.798 N, 6.927 E to 50.809 N, 6.965 E) matches it by position and heading.
- Good for: short hard intervals close to home; not for steady state.

### C6: benchmark segments (moved to claude/segments.md on 6 Nov 2026)
- Segment definitions, PRs and every tracked effort now live in claude/segments.md (built by `segments_tool.py`); the notes below are the older list, all of it now in segments.md.
- Kurfürsten Sprint (0.48 km, 43 s) 305 W; VochemBerg III (0.56 km, 4.9%, 1:25) 277 W; Flammgasse Climb (Bornheim, 0.57 km, 9.8%, 2:16) 270 W; Mount Phantasialand (1.56 km, 3.5%, 3:41) 248 W; Raus aus der Stadt (1.16 km, 1:55) 246 W.
- Kierberger Sprint (0.74 km): 279 W in 1:15 on 17 Oct (271 W in 1:09 on 27 Sep is still the best time).
- Theodor-Heuss Downforce (1.27 km descent): 256 W in 1:43 (27 Sep).
- Mühlenbach Climb (0.77 km, 4.2%): 192 W in 2:27 on 17 Oct, the first effort with a power meter (earlier 2:35 at about 169 W, estimated).
- Fischenich Ahoi (1.58 km, 3.5%): 4:42 at about 189 W (Aug, no power meter then).
- Fischenich Berg (1.05 km, +51 m): 175 s at 257 W (17 Oct): in segments.md since 8 Nov.
- Fischenich Berg Gleise -> Ampel (0.85 km, +42 m): 143 s at 261 W (17 Oct, PR 2:23): in segments.md since 8 Nov.
- Die UtkDoe Challenge (0.94 km, flat): 76 s at 283 W (8 Oct, PR).
- Not yet attempted: Vochem (8704202, 1.44 km, 3%; [Pat 8 Nov] the relevant one, not Vochem Climb) and the steep climbs (Venusberg "Die Mauer", Stationsweg Kreuzberg, Jennerstraße Climb, Climb zur Jugendakademie and 16 more in Bonn, Bornheim, the Siebengebirge and the Ahr valley): all in the to-do list of segments.md since 8 Nov.

### Special courses

### C13: "segments to pr (60 s - 4 min)" (komoot tour 3312761158)
- Type: loop from home, 36.5 km, +234/-236 m, steepest 500 m +7.5%; 40 sharp turns (1.10/km); longest straights 4.1 km NNW (from km 12.2), 3.7 km S (from km 0.1), 2.7 km NW (from km 18.2).
- [Pat] Made for the 27 Sep segment challenge at the end of the 4-week sprint plan: PR attempts on segments near the 90 s goal duration with very easy riding in between; he did not ride all of them in the order of the route.
- Good for: segment hunting (60 s-4 min efforts); not for everyday rides.
- Status: ridden once (27 Sep, segment challenge).

### Strava saved routes (S, from the Strava export of 27 Oct)
Starred in Strava in August (18) and September (1); all start at or near home except S2 and S10. Not analysed in depth. Duplicates of existing entries are kept here only as a pointer (S4 = U4, S12 = C20).

| ID | Name | km | Ascent (m) | Start from home (km) | Sharp turns | Longest straight | Overlaps |
|---|---|---|---|---|---|---|---|
| S1 | Recovery Balance Gravel 30km | 29.4 | +169 | 0.0 | 27 | 3.2 km S | Same area as S3, S7, S11 |
| S2 | Leversbach | 101.0 | +511 | 7.8 | 32 | 15.7 km NE | - (top 330 m) |
| S3 | Threshold Endurance 32km | 31.8 | +187 | 0.0 | 27 | 4.3 km ENE | 80-86% shared with S1 |
| S4 | 10km progressive run | 10.0 | +74 | 0.1 | 16 | 1.5 km NNE | = U4 (run) |
| S5 | Threshold Sprint 10km 2 | 10.0 | +23 | 0.0 | 7 | 4.1 km N | - |
| S6 | Endurance Short 33km | 32.8 | +75 | 0.0 | 23 | 6.4 km SE | - |
| S7 | Recovery Balance 22km | 21.8 | +96 | 0.0 | 23 | 2.7 km ENE | Lies entirely on S1, S3 and S11 |
| S8 | Endurance Short 50km | 50.3 | +224 | 0.1 | 33 | 4.4 km WSW | - |
| S9 | Endurance Gravel 31km | 30.9 | +151 | 0.0 | 24 | 7.1 km SSE | - |
| S10 | Rhein ride | 28.1 | +6 | 9.4 | 3 | 13.0 km S | Rhine out-and-back (13 km each way) |
| S11 | Endurance Balance Gravel 40km | 40.1 | +172 | 0.0 | 29 | 4.0 km SSW | Contains S7 |
| S12 | Threshold Sprint 10km | 9.9 | +70 | 0.1 | 11 | 2.1 km S | = C20 (about 90%) |
| S13 | Threshold Short 15km | 15.1 | +112 | 0.0 | 14 | 2.6 km WSW | - |
| S14 | VO2 max intervals 32km | 32.0 | +176 | 0.0 | 17 | 5.1 km S | - |
| S15 | Threshold Endurance 1h10min | 29.6 | +129 | 0.7 | 18 | 8.3 km NNE | 82-97% shared with S17 |
| S16 | Recovery Balance 26km | 25.8 | +59 | 0.0 | 16 | 5.3 km NNE | - |
| S17 | Threshold Endurance 28km | 27.6 | +80 | 0.0 | 17 | 8.3 km NNE | See S15 |
| S18 | Threshold Balance MTB 20km | 19.4 | +144 | 0.6 | 25 | 2.3 km SSE | - |
| S19 | Threshold Short 13km | 12.9 | +34 | 0.0 | 12 | 3.4 km W | - |

## RUNNING

### U1: Schlosspark Brühl loop (main course)
- Loop of about 1.265 km by GPS (Strava/Samsung just above 1.25 km, komoot 1.30 km), flat, mostly gravel, a few sharper turns (about 3 per lap), no crossings or stops; start 2.4 km from home (50.8249 N, 6.9111 E). 4 laps are about 5.06-5.1 km: time the 5.0 km mark or let Strava pick the best 5K. Pacing per km only. Wet leaves and roots make the sharp turns slippery.
- Good for: 5K trials, hard runs, easy runs and the weekly long run (from 10 Nov, +1 lap a week): one lap takes about 7:35 at 6:00/km, so 6 laps about 45 min, 7 laps about 53 min, 10 laps about 76 min. On long runs the sharp turns add up: keep them easy on wet leaves.
- Status: the regular course (5K trial 23:30 on 28 Oct; first long run 10 Nov: 4 laps at 6:00/km, cut short when the phone battery died; next 6 laps).

### U2: Heider Bergsee 5 km loop (komoot "heider bergsee 5k loop", tour 3353737868)
- 5.00 km, +30/-20 m, steeper ups and downs; harder than the Schlosspark.
- Good for: easy runs; not for a 5K trial.
- [Pat] Ridden several times on the MTB; best full lap 11:40.

### U3: Heider Bergsee 10 km loop (komoot tour 3372509723)
- Loop, 10.0 km, +53/-53 m, steepest 500 m +2.5%; start 2.2 km from home (50.8309 N, 6.8707 E); 16 sharp turns, longest straight 1.3 km.
- Good for: a long easy run with small ups and downs; not for fast running.

### U4: house loop 10 km (strava_10k_house_loop.gpx; Strava saved route S4 "10km progressive run")
- Loop from home, 10.0 km, +72/-78 m, steepest 500 m +4.6%; 16 sharp turns, longest straight 1.6 km.
- [Pat] Roads to the forest/lake area, then gravel paths, then roads and paved paths back home.
- Good for: a 10 km run from the door.

## Template for new routes
```
### <ID>: <name> (<source: komoot tour id / file name>)
- Type: loop|point-to-point|out-and-back, distance, ascent/descent, steepest 500 m, highest point; start (coordinates, distance from home)
- Geometry: sharp turns, longest straights (km, heading, grade), climbs
- Wind: effect of south and west winds on the longest straight
- [Pat] notes (surface, crossings, traffic only when he mentions them)
- Good for / not good for
- Status: ridden on <dates> / not ridden yet
```

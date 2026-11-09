# geo0261 RTK field practice: control points at the Green Fab Lab

**Tool:** Emlid Reach RS2+ or RS3 with the Emlid Flow app; GCP panels, pegs, survey nail · **Time:** the whole field session outside (≈ 3 h, together with the drone flights) · **Builds on:** slides `geo0260_GNSS` (*SAPOS NRW: what you enter in the app*, *A good RTK measurement*, *What the CSV tells you*) and `geo1260_Drone_Imagery_WebODM` (*Control*) · **Groups:** two (or three) groups, one receiver each

You measure points the way you will measure the ground control and check points for the drone flight: only with a FIX, each point twice – once with corrections from SAPOS, once from our own base station on a survey nail you set yourselves. Both groups measure the **same** points, so we can compare two receivers and two measurement times afterwards.

## Before you go out (at home, before the field day, 10 min; check it at the start on site)
1. Note your group's receiver on the list (group → receiver serial number). The teacher has started **raw data logging** on every receiver (RINEX 3, 1 s); do not switch it off.
2. In Emlid Flow, create a project `groupNN` (NN = your group number):
   - coordinate system **ETRS89 / UTM zone 32N** (EPSG:25832), heights **DHHN2016** (NHN);
   - antenna height = pole length as written on the pole (Emlid Flow adds the antenna offset itself).
3. Corrections: NTRIP, caster `sapos-nw-ntrip.de`, port `2101`, mount point `VRS_3_4G_NW`, send position to the caster (NMEA GGA) **on**. User name and password: from the teacher on the day. They are personal to the course: never write them into a notebook, a screenshot or git.

## Outside
1. Switch on, wait until the receiver shows **FIX** in an open spot (no walls, cars or trees nearby). Note the time to the first fix.
2. **Lay out the panels** (group 1: G1–G5, group 2: C1–C3 after setting the nail, step 4). Choose each place with the rules from the slide *How many, and where?*: GCPs at the edges and in the middle of the flight area, check points between them; open sky; **no shadow at flight time** (the November sun is low: stay away from the building and the trees); flat ground. Show the place to the teacher, then lay the panel flat, fix all four corners (pegs on grass, weights on paving, the pattern stays free) and put its label next to it. Then check the other group's panels. From now on **nobody touches a panel** until the teacher collects them at the end.
   Points: measure the panel **centres** (G1 … G5, C1 … C3), pole tip in the centre mark. Name them exactly like that in Emlid Flow, and take a photo of each panel with its label.
3. At every point: pole tip on the point, pole vertical (bubble), wait for FIX, then **average for 30 s**. Do not accept a FLOAT or SINGLE solution. Note anything special (e.g. "next to a tree").
4. **Base mark B1**: our own survey mark for later flights, in a paving joint between the concrete blocks along the northern edge of the central lawn, south of the Green Fab Lab (the teacher shows the place and brings hammer, nail and paint). If it is not set yet, one group sets it: survey nail into the joint until it is flush with the paving, a paint ring around it. Then both groups measure it with SAPOS as point `B1` **first**. Take a photo of the nail with something for scale and sketch where it is (distances to two fixed objects). The first `B1` value is typed into our own base station (Reach RS3), which then stands on the nail.
**During the mapping flights nobody stays in the flight area:** wait at the take-off spot and fill in the flight log (geo1262). Panel work and flights take turns.
5. **Round 1 – SAPOS:** measure all points as described in steps 2–3.
6. **Round 2 – our own base:** at least 15 min later, switch the correction input in Emlid Flow from NTRIP (SAPOS) to **LoRa** (settings from the teacher) and measure every point **again** (names `G1b` …, `C1b` …). Now the corrections come from our base on B1, not from SAPOS: this is the differential principle (geo0260 *Your own base station*).
7. **Experiment *wrong base*** (with the teacher, ≈ 5 min): the base coordinate is typed in 1.00 m too far east. Measure one panel. Where does it end up? Then the correct value is typed in again; measure the panel once more.
8. **At the end:** when the base has been taken off the nail, both groups measure the nail again with SAPOS as `B1b` (as late as possible).
9. Stretch (optional): the height benchmark **4405900316** at the Große Goorley bridge (bolt set sideways into the wall, H = 25.089 m DHHN2016, levelled 2022). Measure an RTK point on the ground directly below the bolt and the height difference to the bolt with the tape. Does RTK + tape give the benchmark height?

## Before you leave the site
- Export the points from Emlid Flow as **CSV ("All columns")** and save it as `groupNN_emlid.csv`.
- Upload the CSV to Moodle (assignment for this session) **before you leave**.
- Give the receiver back to the teacher (the raw log is downloaded from the receiver).

## Back in the room (10 min)
- Open your CSV: all points FIX? RMS values? How far apart are round 1 (SAPOS) and round 2 (own base) at each point? Is the difference about the **same at every point**? What does that tell you about the base coordinate?
- The experiment: by how much did the panel move when the base was 1.00 m wrong, and in which direction?
- Compare one point with the other group: by how many centimetres do the two receivers differ?
- `B1`: write the four SAPOS values (two groups × two times) in a small table. Do they agree within 2 cm? Their mean becomes the base mark coordinate (E, N, ellipsoidal height and DHHN2016 height: keep both). How far is it from the preliminary value the base used today, and does that match the round 1 – round 2 shift?

## Notes
- Your field data stay in the course: hub folder `~/shared/data/opengeo/geo0264/groupNN/` and Moodle, not in the public release repository.
- The raw logs and your CSV are used later: optional notebook `geo0264` (your own position from pseudoranges, `SOURCE = "own"`) and the accuracy check of the drone products.

## Sources
- SAPOS NRW user information (Bezirksregierung Köln, Geobasis NRW): caster, mount points.
- Height benchmarks NRW (Höhenfestpunkte, AFIS), Geobasis NRW, dl-de/zero-2-0.
- Emlid Flow documentation (docs.emlid.com).

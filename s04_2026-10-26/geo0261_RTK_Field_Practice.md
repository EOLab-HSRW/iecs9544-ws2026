# geo0261 RTK field practice: control points at the Green Fab Lab

**Tool:** Emlid Reach RS2+ with the Emlid Flow app · **Time:** about 60 min outside · **Builds on:** slides `geo0260_GNSS` (*SAPOS NRW: what you enter in the app*, *A good RTK measurement*, *What the CSV tells you*) and `geo1260_Drone_Imagery_WebODM` (*Control*) · **Groups:** two groups, one receiver each

You measure points the way you will measure the ground control and check points for the drone flight: with SAPOS network RTK, only with a FIX, each point twice. Both groups measure the **same** points, so we can compare two receivers and two measurement times afterwards.

## Before you go out (in the room, 10 min)
1. Note your group's receiver on the list (group → receiver serial number). The teacher has started **raw data logging** on every receiver (RINEX 3, 1 s); do not switch it off.
2. In Emlid Flow, create a project `groupNN` (NN = your group number):
   - coordinate system **ETRS89 / UTM zone 32N** (EPSG:25832), heights **DHHN2016** (NHN);
   - antenna height = pole length as written on the pole (Emlid Flow adds the antenna offset itself).
3. Corrections: NTRIP, caster `sapos-nw-ntrip.de`, port `2101`, mount point `VRS_3_4G_NW`, send position to the caster (NMEA GGA) **on**. User name and password: from the teacher on the day. They are personal to the course: never write them into a notebook, a screenshot or git.

## Outside
1. Switch on, wait until the receiver shows **FIX** in an open spot (no walls, cars or trees nearby). Note the time to the first fix.
2. **Points:** the teacher shows the points (P01 … P06): sharp, flat features such as paving corners, manhole cover centres or nails. Name them exactly like that in Emlid Flow. If ground control panels are already laid out, measure the panel **centres** (G1 … G5, C1 … C3) instead.
3. At every point: pole tip on the point, pole vertical (bubble), wait for FIX, then **average for 30 s**. Do not accept a FLOAT or SINGLE solution. Note anything special (e.g. "next to a tree").
4. When all points are done, measure every point **a second time**, at least 15 min after the first time (name `P01b` …). The satellite geometry has changed in between.
5. Stretch (optional): the height benchmark **4405900316** at the Große Goorley bridge (bolt set sideways into the wall, H = 25.089 m DHHN2016, levelled 2022). Measure an RTK point on the ground directly below the bolt and the height difference to the bolt with the tape. Does RTK + tape give the benchmark height?

## Before you leave the site
- Export the points from Emlid Flow as **CSV ("All columns")** and save it as `groupNN_emlid.csv`.
- Upload the CSV to Moodle (assignment for this session) **before you leave**.
- Give the receiver back to the teacher (the raw log is downloaded from the receiver).

## Back in the room (10 min)
- Open your CSV: all points FIX? RMS values? How far apart are the first and the second measurement of each point?
- Compare one point with the other group: by how many centimetres do the two receivers differ?

## Notes
- Your field data stay in the course: hub folder `~/shared/data/opengeo/geo0264/groupNN/` and Moodle, not in the public release repository.
- The raw logs and your CSV are used later: optional notebook `geo0264` (your own position from pseudoranges, `SOURCE = "own"`) and the accuracy check of the drone products.

## Sources
- SAPOS NRW user information (Bezirksregierung Köln, Geobasis NRW): caster, mount points.
- Height benchmarks NRW (Höhenfestpunkte, AFIS), Geobasis NRW, dl-de/zero-2-0.
- Emlid Flow documentation (docs.emlid.com).

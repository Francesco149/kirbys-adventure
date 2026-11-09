# Recipe for autonomous TAS discovery: what I learned from a full Kirby's Adventure run

Kirby's Adventure (NES, USA Rev A) on FCEUmm. The run was power-on to Nightmare Wizard killed (f136812), reaching the ending scene at f137529. It took 63 episodes and about $78. The movie replays from power-on and was verified at every milestone. The sections run in the order a future agent should do things. Each claim names the segment or episode it was measured in.

## 0. Results at a glance
| part | frames | cost | f/$ | method |
|---|---|---|---|---|
| Worlds 1-4 and the first half of 5 (replay of reference 3226M) | 78,090 | ~$0.2 | ~400,000 | lab replay, then `play` in chunks of 3600 frames |
| My own first pass at 1-1..1-4 (thrown away) | — | ~$8-15 | — | search + manual, before I knew the reference synced |
| Routine stages with a fresh context (6-1, 6-5, 7-3, 7-5) | 2.4-3.6k each | $0.75-1.0 | 2,400-3,600 | roominfo, then one search per room |
| Stages at the end of a long context (6-2, 7-2) | 3.7-3.9k | $3.4-5.9 | 650-1,150 | same method; turns cost 5x more |
| Bosses and diagnosis (Meta-Knights, Orb, Wizard) | 0.4-2k each | $0.3-3.5 | 300-1,000 | random search, lab controllers |
| Whole run | 137.5k | ~$78 | ~1,770 | |
The target was ≥3,000 f/$. Routine own play with a fresh context meets it. Long contexts, bosses and diagnosis do not.

## 1. Before you play anything (these rules would have saved the most money)
1. **Test every reference movie in the knowledge base against your core first.** In the lab, replay it from power-on and log (frame, room, hp, lives) whenever they change. The point where it desyncs is the first room that lasts implausibly long, where lives drop, or where x freezes. 3226M (made for PRG0) synced on PRG1/FCEUmm until 5-6 room 1. I skimmed past the KB note saying so for 4 episodes and lost about $8-15 redoing worlds 1-4, ending about 6,000 f slower. The replay test costs 118 s and $0.05.
   - After the desync, repair with one search (a door overshoot of 37 px). Then try re-attaching the reference at about 100 offsets in the lab: it never re-synced here, because RNG and positions had already diverged.
2. **Read the KB file headers completely.** Each one is a paragraph long.
3. **Find the RAM.** Pre-seeded vars plus mark/diff. Verified for Kirby:
   - room / trans: trans 0->1 at a door, 0->4 on a hub return, 0->5 on a stage clear.
   - hp: it reads 255 while dying.
   - Boss HP is the $61CA+slot table entry equal to the known HP when the fight starts. That table also holds projectile values.
   - Object slots: class at $6200+s; X at $6074/$6086+s; Y at $6098/$60AA+s.
   - Collision map: W/H at $67EE/$67EF; tiles at $68C8+screen*192; attributes at $7F00. **The solid attribute values differ per tileset**, so print a legend.
4. Build two lab helpers once:
   - `roominfo`: ASCII collision map with a legend of every attribute value and door pixel coordinates.
   - A goal-game / cutscene scan: loop over the press frame k from a checkpoint and measure the frames until the next room (18-35 s).

## 2. Per-room routine (traversal) — about 3 turns per room
1. `play .*30`, save a checkpoint, run roominfo — one turn.
2. One search to the door — one turn.
   - **Open or slope rooms:** built-in beam search, beam 256-512, depth 55-70, 8-frame actions. Use [R*8, UR*8, DR*8, U*8, D*8, L*8, "U*5 .*3" (door), ". B*12 .*2" (laser)].
     - Score: -2|x-dx|-|y-dy|. Goal: room change.
     - Avoid: `hp<N or hp>47` (hp>47 catches the 255 death value) and `room==<entry room>`.
     - Typical yield: 200-600 f per call, 40-120 s.
   - **Maze / blocked / breakable rooms:** lab `runflow2.py`. It is a parallel beam whose score is a Dijkstra distance field from the door over the collision map, recomputed each time the tilemap changes (blocks broken).
     - Pass SOLIDS for the tileset and ACTS that include shot macros.
     - Results: 6-4 room87 took 1,184 f in one call where 3 built-in calls had stalled. 7-4 rooms 149-153 took one call each (140-602 f).
3. Apply the result, then go to the next room. The goal game / cutscene press frame comes from the lab scan (k varied 54-58 across stages, so always rescan).

Score-design failures I hit more than once (each cost 1-3 stalled 120-s searches):
- A piecewise score must be continuous and monotone along the path. The next phase's base must sit above the previous phase's maximum. A zigzag shaft works with `band*1000 + progress_in_band`.
- Pure `score x` takes whichever branch goes furthest right; it took a wrong corridor in 1-2 room50. Constrain it with avoid on y, or use the distance field.
- A score-only apply appends the full depth after progress saturates. Always give a goal.
- If the best x doesn't move, Kirby may be physically pinned. Look at a strip before searching again (6-3 room82, 7-3 room144: a manual 2-call nudge fixed it).
- The door mechanics depend on the character state. UFO needs Up held for about 5 f; `U .*2` never triggered it. I found this by reading the reference's inputs at a door.

## 3. Fights
- **Mid-bosses (one target, short):** one random-mode search, samples 4000, depth 12.
  - Actions: whole-shot macros [B*68 .*2, B*36 .*2, ". B*12 .*2", "R B*67 .*2", "R B*11 .*2"] plus 8-f moves. Goal: HP slot == 0.
  - Results: 98-131 f per mid-boss and about 60 s; it worked first try 6 times (7-2 ×4, Grand Wheelie, Frosties).
  - 8-frame B actions never charge a 65-f shot, so macros are mandatory.
- **Multi-enemy or unpredictable fights:** random mode with one kill or hit per call (goal = HP ≤ next step), not beam.
  - Meta-Knights: beam stalled 3 times at 100-230 s each. Random mode got 65-103 f per kill.
  - Beam dedupes onto one cluster when the score is flat between kills.
- **When a random search finds nothing:** lengthen the horizon (16/32-f waits, depth 45), add hover-shot macros, change the seed, loosen avoid. Wizard hits 2 and 5 failed at first; each was fixed this way.
- **Cooldown-bound grinds** (Nightmare Orb, 60 hits of 1 damage): both search modes failed.
  - What worked: a 30-line lab greedy controller. It aligns y to the boss object slot, holds an x target, and mashes B. A 24-f savestate shield vetoes any hp loss.
  - A 6-run sweep of the x target took the Orb from 3312 to 1952 f in 2 minutes.
  - The same controller with xt=200 solved the post-Orb chase (768 f).
- **Before searching a boss, log long enough.** The Wizard HP only fills 1330 f into the room. Lab runs of 1600 f missed it, which cost about 6 short episodes.
  - Checkpoint at the frame the bar fills.
  - Identify the phases (cutscene, flee, fight) from object slots plus a strip.

## 4. Controllers compared (Experiments 1-5, same checkpoints)
Rooms: 7-3 rooms 145 and 144, 7-4 room148. UFO, hp=7 (one hit kills). The table gives frames to the exit.
| controller | r145 | r144 | r148 | cost |
|---|---|---|---|---|
| built-in beam search | 561 | 715 | 555 | 2-4 turns |
| flow-greedy | died | stuck | died | $0 |
| RF clone (650 samples, with the flow hint) | 624 | 672 | died | $0, trained in 2 s |
| Jev with the hint | died | timeout | died | $0.003 |
| shield + flow | 888 | timeout | 936 | $0 |
| shield + RF | timeout | 672 | 784 | $0 |
| shield + Jev with the hint | 1448 | timeout | 880 | $0.03 |
- Offline agreement with search labels (160 states):
  - Jev without the hint: 0.56 (soft agreement).
  - Jev with the hint: 0.73.
  - The hint feature alone: 0.74.
  - Always pressing right: 0.51 (exact agreement).
- Verdict:
  - Reactive policies die without lookahead, so a shield is mandatory.
  - Even shielded, they are 1.2-2.6x slower than search.
  - Jev adds nothing beyond the feature it is fed.
  - The tiny RF clone beats Jev at zero cost.
  - Controllers pay off only as hand-written, task-specific greedy controllers for grinds (Orb), or as rollout priors inside search.

## 5. Cost management
- Turn cost rises with context: about $0.03 early in an episode, $0.16-0.3 after about 700 turns. 7-3 cost $0.95 in a fresh episode; the comparable 7-2 cost $5.9 at the end of a long one.
- **Milestone or hand off at every stage clear. Keep the notes compact. Use view=none once the routine is trusted.**
- A stage counts as cleared only by its RAM transition (goal-game room, then trans 0->4), never by a screenshot. In 7-6 I took the wrong last door and milestoned a fake hub, which cost about $1 and 2 episodes.
- Short episodes of 2-3 turns, each ending in "NEXT: ...", made progress very slowly in the endgame (ep43-61: about 19 episodes for 2 bosses). Better: give each episode enough budget to finish one full diagnosis-then-act loop.

## 6. Harness wishes (concrete)
1. A built-in `search` score `distance_to=(x,y)` that uses the room's collision flow field, recomputed when the tilemap changes. It would turn every maze room into one call.
2. A `rollout(policy, shield_frames)` primitive, and search seeded by a policy prior.
3. A milestone RAM predicate, e.g. "trans went 0->4 within the last N frames".
4. An object-slot viewer: per-frame class/x/y/hp table for all 18 slots over a frame range.
5. Automatic truncation or summarisation of old tool output, to keep turn cost flat.
6. Lab rendering that works out of the box. `c.step` returned an image or None inconsistently, and `c.render` is a flag.
7. A per-tileset collision legend in the RAM map.
8. A `play` limit above 3600 frames per call, or a "replay reference file from frame a to b" command.

## 7. Open optimization opportunities (not done)
- Orb: try leading the shots, or seed a beam with the greedy controller.
- Wizard: re-search hits 2/4/5 (368/387/555 f) with more seeds.
- Bonkers in 6-3 (453 f vs ~110 f with the template).
- Hub idle waits (.*240 per stage): scan the earliest frame that accepts input.


## 8. Addendum (ep66-67): what re-seeding a found hit gains
- I re-ran Wizard hit 5 from 8-wiz-khp20 with seed 11 and the same settings: 554 f, against the original 555 f, for about $0.3 of turns. Re-seeding a random search on a hit it has already found gains about 0 frames. Spend optimization budget on structural changes instead: a different strategy, alphabet or controller, or route-level skips. So the "re-search Wizard hits" item in §7 has low value.
- I stopped here with about $20 left and kept that reserve. The movie stays at ms-final, f137712.


## 9. Addendum (ep82): hub unlock idle, lab-only scan
- From ms-7-1 (W7 hub, just arrived) I waited k frames, then held UR for 20 f and logged dx/dy. Response by k: 0-10 is a scripted drop (-56/-560); 20-160 gives dx 0 / dy 0 or scripted wobble (the cutscene ignores input); 170-200 shows scripted motion; **from k=210 on the response is the same steady (+8,-4)**. So input is probably accepted from about k≈205-210, not 240. That would save about 30 f per stage start, or about 400 f over the ~13 hub starts after the first one.
- This is UNVERIFIED in the movie. Before using it, scan k in 200-240 by applying the real door inputs and measuring the frame the room changes. It was not applied, because changing an early hub wait would desync everything after it.

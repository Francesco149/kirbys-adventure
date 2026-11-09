# Validation report (w12-scratch)

| segment | frames | $ | notes |
|---|---|---|---|
| boot+1-1 | 3713 (hub return) | ~2.42 (incl. building auto.py/drive.py lab tools) | 1-1 room 43 took 1063f with 2 hits |

## Recipe corrections so far
- Lab background jobs using multiprocessing need `if __name__=='__main__':` guard (spawn).
- room var is stale ~25 frames after a room change; wait before reading room data.
- Without a room `order`, generic "any new room" goal takes side doors (1-1 room 44 -> side room 46).


| 1-2 partial (hub->Poppy Sr kill) | 3713->6700 (2987) | ~2.1 | drive.py failed in room 47 (warp-star 'door' at top); built-in x-score search worked; Poppy Sr with normal Kirby needed random mode (beam stalled 3x), ~1060f, entered fight at hp7 |
- Correction: recipe's mid-boss template assumes UFO; for normal Kirby vs Poppy Sr use random depth 30-40 with inhale/spit macros, one hit (10 dmg) per call.
- Correction: background lab jobs don't run in the lab cwd; add sys.path/chdir.


| 1-2 complete (hub->hub) | 3713->8966 (5253) | ~2.8 total (last part room 49 door->hub: 2266f for $0.55, 23 turns = 4100 f/$) | routine rooms with built-in search + one flow2 call held as written |
- Correction: labkit API is `lab.load(ck)` (not core(ck)); flow2 needs a script file + subprocess (spawn guard).


| 1-3 (hub->hub) | 8966->12839 (3873) | ~1.13, ~29 turns (~3400 f/$) | hub door 1 search call; room 53 built-in beam stalled twice at a hill wall (cost ~550 wasted frames + $0.1), flow2 then 288f in 1 call; rooms 54-56 flow2 one call each (+1 short built-in door search). Goal game .*56 A |
- Correction: with hp at 1 bar (avoid hp<7) the built-in score beam stalls behind enemies/walls; make flow2 (generic fl.py wrapper) the default, not the fallback. flow2 paths are float-heavy (~1.3-1.5 px/f) but reliable.
- Correction: hp does not refill on entering a hub/stage (stayed 7 from 1-2 to 1-3 end).
- Note: search actions with quotes failed ("bad input spec") — fixed by owner mid-run.



| 1-4 (hub->hub) | 12841->17049 (4208) | ~1.71, 37 turns (~2460 f/$) | hub door search 1 call (119f). Room 57: built-in stalled (Kirby pinned in tree notch under ceiling), flow2 goal y<115 1 call. Frosty: random mode 2 calls (fhp $61D8). Room 58 flow2 744f for ~720px (slow floating) — built-in finished last 145px faster. Room 59 (vertical trunk) flow2 520f 1 call. Room 60 built-in stalled twice (my y>170 avoid forbade needed lower path), flow2 finished. Goal game .*53 A |
- Correction: in open horizontal rooms flow2 floats (~1 px/f); built-in beam is ~1.7 px/f. Use built-in first for open rooms, flow2 for vertical/blocked.
- Correction: never constrain y in avoid unless checked against the map; the walkable path may dip below.
- Correction: search `apply` appends trailing actions past the goal frame (e.g. R*27 after room change); harmless but wasteful.



| Whispy (hub->W2 hub) | 17049->20222 (3173) | ~0.85, 30 turns (~3700 f/$) | hub boss-door: first search targeted the wrong 'door' (roominfo lists warp-star tile 456,73), second (440,153) 152f. Room 8 drops 2 floors to arena (manual). Whispy HP at $61D4 (bar fill ~120f). 6 random-mode calls (normal Kirby, spit star 10 dmg) 52-259f each, fight 1100f incl. intro. Piece catch + cutscene ~1000f. |
- Correction: hub `roominfo` door list includes non-door tiles (warp star); confirm by screenshot. Recipe's boss template (UFO piercing) n/a for normal Kirby; random mode one hit/call worked 6/6.
- Note: the unnecessary 300f hub wait (step was satisfied at room entry) - boss door unlocked right away; scan the hub wait instead of guessing.



| 2-1 (W2 hub->hub) | 20222->23333 (3111) | ~0.81, 20 turns (~3800 f/$) | hub door search 84f (input accepted right after hub fade, no 240f wait needed). Room 169: built-in beam stalled (coconuts / ~x590), flow2 1 call 640f to door. Room 170: built-in stalled at x~740 (tall rock), flow2 752f to tower top, then built-in finished 212f. Room 172: built-in score-only path then 83f door search. Goal game .*56 A (goalscan). |
- Measured: built-in beam with goal fails in 3/3 2-1 rooms within depth 70 (rooms ~1000px wide need >70 8f actions); score-only partial + second short call works. Recommend: depth to cover room width/1.5px per frame, or chain calls.


| 2-2 partial (hub->room 175) | 23355->24715 (1360) | ~1.5 so far (ep 10, long context) | hub door 1 search + 1 entry search. Room 174 bomb block: 6 turns of diagnosis wasted (puff/inhale tests) until a random search with goal "map tile byte changed" found slide = D*4 A*4 in 37 s. Room 175: roominfo door not reachable (camera stall); a Warp Star is the exit - roominfo doesn't list it. |
- Recipe addition: for bomb/breakable blocks, search goal on the tile byte `ram[0x68C8+idx] != v` (random mode, attack macros incl. "D*4 A*4" slide) instead of guessing.
- Recipe addition: roominfo door list misses Warp Stars; when flow2 stalls toward a listed door, look at the screen for a star.



| 2-2 (W2 hub->hub) | 23355->28768 (5413) | ~3.2 (eps 10-11; ep 11 alone 175->hub 4050f for $1.1, 38 turns = ~3700 f/$) | Room 175 Warp Star: touch while floating, ride ~460f (I idled ~300f extra before noticing). Grand Wheelie (no UFO): 3 random-mode calls 175/360/359 f, cost 24 hp. Room 176 second bomb block: beam with tile-byte goal found it in 11 s. Room 177 door needed 2 Up taps. Goal game goalscan k=20. |
- Correction: Warp Stars are objects, not doors: read slot positions (class/x/y tables) and target them; built-in search then reports no goal because riding is not a room change for ~300 f — use goal `trans != 0` or just play .*N after contact.
- Correction: the built-in beam stalls (score unchanged) when Kirby is pinned against a step while floating; a manual "(R*20 RA*10)xN" climbed it. Include RA in alphabets and check vx/x over a lab rollout before re-searching.


| 2-3 partial (hub->Meta-Knights room 180) | 28768->31854 (~3090) | ~1.8 (ep 12, 40 turns) | hub unlock cutscene ~240f; first hub door search failed (input not accepted during cutscene). Room 179: flow2 distance field unreachable because flowsearch treats ladder tile 0x23 as one-way (blocks the downward path) -> patched fs.ONEWAY={15} (fly2.py), then 1 call 380f. Room 181 pond: flow2 stalled trying to go over a pillar top; intermediate target under water fixed it; swim slow (592f). |
- Correction: flowsearch ONEWAY includes ladders (0x23) and makes ladder-down routes unreachable; remove 35 from ONEWAY.
- Meta-Knights (normal Kirby): random search goal on shared bar (bhp<44) found nothing in 4000 samples depth 35.


| 2-3 Meta-Knights room 180 | 31854->33537 (~1680 incl. 120f intro) | ~1.1 (ep 13, ~25 turns) | random mode one bar step (5) per call, 11 successful calls 62-244 f; 4 failed calls when remaining knights sat on top platforms (solid from below; Kirby must go round the platform edge) - fixed by a short beam to above the platform (143f), then random kills resumed. |
- Correction: for Meta-Knight ambushes with normal Kirby, goal = shared bar decrease by one step (bhp<prev), depth 25; if 2 calls fail, check where the knights are (strip) and reposition first. Recipe's "random mode, one kill per call" held.



| 2-3 (W2 hub->hub) | 28768->34660 (5892) | ~3.4 (eps 12-14) | ep 14 (room 180 door ->hub, 1000f, ~$0.3, 10 turns): room 180 exit door appears under the middle platform; built-in door search stalled twice (Kirby still puffed, needs B to deflate; score monotone failure going round a platform edge) -> manual L*44 then search with "B .*3" action found 139f. Room 182 built-in beam depth 60 one call 355f. Goal game goalscan k=56. |
- Correction: after a boss/ambush Kirby may be floating; include "B .*3" (deflate) in door-search alphabets.



| 2-4 partial (hub->room 185) | 34660->39007 (~4350) | ~1.5 (ep 15) | Wrong hub door: (344,249) is the Crane Fever minigame, not 2-4: ~2650f + ~$0.7 lost (it refilled hp though). The 2-4 door sits on a cloud that is solid from below; the beam stalled under it. Manual go-around fixed it. Room 184: built-in beam stalled at once; fly2 took 972f in 1 call (6 min wall time); door search 103f. |
- Correction: confirm hub door identity (number sign over the door) with a screenshot before searching; roominfo lists minigame doors too. The stage var does not update after the minigame.



| 2-4 room 185-189 (ep 16) | 39007->41394 (~2390) | ~1.3, ~40 turns | roominfo right after entry showed the stale previous-room map -> built-in beam & flow2 aimed at a door behind a camera lock (Tick-Tock arena); 720 f of flow2 partly wasted. Tick-Tock: random mode 3 hits (546 f incl. a failed-call wait). Post-kill Kirby slowed until D pressed. Rooms 186, 188 built-in door search 1 call each (176 f, 143 f). |
- Correction: mid-boss arenas lock the camera/right edge until the boss dies; check boss HP vars at room entry before routing.
- Correction: wait >=45 f after a room change before roominfo (map buffer lags the room var).



| 2-4 (W2 hub->hub) | 34660->43085 (8425, incl. ~2650 wasted in Crane Fever) | ~3.4 (eps 15-17) | ep 17 (room 189 -> hub, 1690f, ~$0.45, 9 turns): fly3/flow2 938f for 900px (floating, took a hit -> hp 7), built-in beam then stalled (bird enemy on the wall top; a manual try died -> rewind); random search goal x>1150 with "B .*3" pellet 230f; door search 127f -> room 189 exit leads straight to goal game room 42 (room 190 not visited); goalscan k=57. |
- Correction: at 1 HP bar, use random-mode goal searches (x threshold + hp==7) rather than beam score; random found a pass in 86 s where beam stalled.



| 2-5 (W2 hub->hub) | 43085->48271 (5186) | ~1.85, ~36 turns (~2800 f/$) | hub: 2-4 unlock cutscene (~240f, camera pans, input ignored) made the first door search fail — roominfo before the cutscene lacked door 5 (the map extends after blocks break). Rooms 191, 192, 194: built-in beam / random stalled at 1 HP (Shotzo, Parasol Dee); fly3/flow2 one call each (736/976/1106 f, 8-10 min wall). Room 196 star-block grid: random search goal y<240 found Starman swallow -> Hi-Jump + climb (227f), beam door search 245f. Room 197: beam with avoid y>175 (pits) + short door search. Goal game k=56. |
- Correction: after a stage clear, wait out the unlock cutscene and re-run roominfo; new doors appear only after it.
- Measured: at 1 HP bar, flow2 is the reliable default for long rooms (3/3 first-try); built-in beam stalls.



| Paint Roller (W2 hub->clear) | 48271->50786 (~2500) | ~1.25, ~36 turns | hub: unlock cutscene 240f; first door search entered the star door (488,121) = mid-boss Arena room 37 (~330f+$0.1 lost); boss door is (696,121), 261f search. Fight: Hi-Jump 8 hits, random mode 1 hit/call; at 1 HP bar the hit-7 state led to unavoidable death (3 failed calls ~$0.2) -> survival rollout in lab then last hit. Piece needs D press then jump. |
- Correction: hub "boss door" isn't the unique special-looking door; the Arena (star door) also exists. Verify stage==7 right after entry.
- Correction: boss random-search goal must exclude death (death resets boss HP var to 0); keep avoid hp>47.



| Paint Roller clear -> W3 hub | 50786->51207 (421) | ~0.05, 2 turns (ep 20) | Level-3 intro screen; after 400 f idle I pressed A once and the hub loaded 17 f later. (Not measured whether the press was needed.) |

## Totals (measured)
- Power-on -> W3 hub (world 2 room 2) at f51207; movie ends f51310. Cost ~$23.8 over 20 episodes, ~2,150 f/$ overall.
- Per-world: W1 + Whispy 20,222 f, ~$9.3 (~2,200 f/$); W2 + Paint Roller 30,985 f, ~$14.5 (~2,140 f/$), including ~2,650 f lost in Crane Fever and ~330 f in the Arena door.
- Main recipe gaps: (1) the UFO-centric fight templates don't fit normal Kirby; random mode with one hit per call was the template that worked on every boss. (2) At 1 HP bar the built-in beam stalls; flow2 or random-mode threshold goals were reliable. (3) Hub door identity: roominfo lists minigame, arena and warp-star tiles as doors; check with a screenshot and check stage right after entry. (4) Unlock cutscenes (~240 f) block input and change the hub map.
- Harness wishes: roominfo should list warp-star objects and mark minigame/arena doors; search should have a built-in "boss HP minus death" goal helper; a flow2 option in the built-in search to save the 6-10 min lab wall time per call.

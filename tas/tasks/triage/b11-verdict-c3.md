# Verdicts for slice C, banks 29 and 2A (batch 11 triage, part c3)

Columns: branch, side never run, target, bytes, unit, routine, verdict, reason / start window.
Input: the 62 rows of banks 29 and 2A in b10-verdict-c.md (all "unsure" there).
Counts: **reachable 41, unreachable 2, unsure 19** (of 62). Bank 29: 20 / 1 / 5; bank 2A: 21 / 1 / 14.

How rooms were found: room object lists (room_objs_* in 12:8A80/8BC7/8D0E) read from the ROM for the kinds, the
door lists (room_doors, 12:923B) for the way in, and `kd when` on each kind byte of a room's list (objs_spawn reads it
when the room loads) to see which movies ever loaded that room. A room the corpus never loaded is marked
"never loaded".

| kinds | type, class (obj_param) | rooms (loaded by the corpus) | rooms never loaded |
|---|---|---|---|
| $B6 / $B7 | $4A beetle, class 0 / 1 | 210 (main@31519), 137 (main@112322) | 124 ($B6, stage route below), 39 ($B7, hub 3), 313 ($B7, demo chain), 312 ($B6, attract only) |
| $B8 / $B9 | $4B shell, 0 / 1 | 258 (main@53092), 135 (main@111877) | 62 ($B8), 122 ($B8), 315 ($B9, demo chain) |
| $B4 / $B5 | $49 wheel, 0 / 1 | 176 (main@15183, 7 screens wide), 164 (main@122430, 1 screen) | 209 ($B4), 38 ($B5, hub 2) |
| $BA / $BB | $4F turtle, 0 / 1 | 185 (main@21393, 2 screens), 200 (main@28265), 268 (cov5-f-del@215118) | 116 ($BA), 129 ($BB, no door leads to 127/128), 316 ($BB, demo chain) |
| $BE / $BF | $4D mane, 0 / 1 | 139 (main@112744) | 126 ($BE), 301 ($BE), 41 ($BF, hub 5) |
| $FE | $6F Big Switch | 66 73 85 89 96 107 112 162 202 233 241 254 270 276 296 300 309 (cov5-f-del, from @158077) | - |
| $6F | $1C runner | 67 (main@85714), 194 (main@24591), ... (69 76 87 214 220 235 261 267) | - |

Ways in (door lists): 126 <- 125 <- ... <- 114 <- room 113's lower door (cell 0, col 8, rows 8-9; main@111314 took
the door at row 2 to 133); the route 114-126 also holds 116 ($BA), 122 ($B8), 124 ($B6), and 126 leads on to 141.
301 <- room 303 (doors at cell 0 col 14 row 9 and cell 2 col 1 row 9; main@76370 in 303 left by the door to 302).
209 <- room 207 (cell 2 col 6 row 8; main@30813 took 208). 62 <- room 61 (cell 4 col 7 row 0; main@82856 took 63).
38 / 39 / 41 <- the hubs 2 / 3 / 5, a door of kind $19 each (by their place, the parts of the hub that a Big Switch
opens: cov5-f-del pressed every switch but entered none of them). 312-316 form the chain 168 -> 312/313 -> 314 ->
315 -> 316 -> 168: rooms of the attract demos (fixed input, demo_number 1-7 never played), not of the game.

## Best leads (play tasks)

1. **Mane mid-boss's burning dash (type $4D, room 139, start cov3-b-e4d@114014; main@112734).** State 9 (e4d_burn,
   after e4d_flame_a) dashes at $0300. (a) Stand closer to the wall it dashes toward (within ~48 px) so the dash meets
   the wall while its pose is $3A-$41: 2A:A140 (in cov3-b-e4d@114051 it met the wall one frame after e4d_away_far,
   pose $42). (b) Stand far from that wall so the dash ends on open floor: the slow-down reaches 0, 2A:A0E8.
   (c) Keep something in the mouth (kirby_form 1) when a lunge catches Kirby: 2A:A801.
2. **Mane class 0 ($BE, never loaded): room 301 (world 5, from room 303, main@76370) or room 126 (world 7, the lower
   door of room 113, main@111314).** Its first plan step is class 0 (2A:A2FF); its lunge2 (state 3, plan step 6 or
   e4d_random_states) runs e4d_param_random with obj_param 0 (2A:A497). The same 113 -> 114 route passes the never
   loaded 116 (turtle), 122 (shell), 124 (beetle class 0).
3. **Grand Wheelie class 1 ($B5, room 164, main@122420; main left after 2 frames).** Let it roll and brake: speed
   $02A0 gives e49_speed_class 2 (2A:AEC2) and a 96-frame brake, longer than variable 6 = $3C (2A:AD2D) if no wall
   comes first; a brake into a wall (2A:AF04) if Kirby is ~70-100 px from it. Its small wheel (every third decision)
   in this walled one-screen room: rolling into a wall (2A:AE89), flying into one (2A:AE61, Kirby near the wall).
4. **Grand Wheelie class 0 (room 176, main@15183, w12-opus@26468).** Kirby left of it when e49_throw's small wheel
   lands: it rolls left (2A:AEA7). A feint (Kirby within 64 px in front) rolling away into a wall (2A:AD75); a brake
   into a wall (2A:AF04). A hit on the wheel's very first tick (2A:AB4E, frame-exact: a shot where it appears).
5. **Beetle (type $4A).** Class 1 (room 137, cov4-a-bug7@112741): attack 1 needs kirby_action 4/5 or $0D at
   e4a_pick (rows 4/5: random 3-4 of 8, or 0-4) -> e4a_hover_count 7 (29:A451). In attack 1 (cov4-a-bugm@60717):
   Kirby at its height but 32+ px away (29:A474), Kirby left of it at the dive (29:A49B), the last hit during the fly
   / dive (29:A4CF) or the leap (29:A4DF). Grabs: no block in the nine points ahead (room 137 facing right,
   cov4-a-bug7@112741) and random 0-3 / 4-6 / 7 after a throw 0 (29:A354, A363, A375); the first grab of a fight
   with the beetle at X >= ~208 (variable 4 still $FF: Kirby is pulled to X + 51, past 256: 29:A5FA). A slide
   (kirby_rect kind 1) into the beetle while it drops in at the start or bounces off a wall (record 39:878C sets
   variable 2 = $FF: 29:AFB0).
6. **Shell mid-boss (type $4B, room 258, cov3-a-turtle@53218 / cov4-a-turtle@53319).** The last hit during e4b_leap's
   hang (29:AC1A) or e4b_leaps (29:AC43); a grab with a wall within ~50 px in front so e4b_spin rolls into it
   (29:ACA3); a no-wall grab after a throw 3 with random 6-7 (29:AB6C).
7. **Turtle (type $4F, room 185, w12-sonnet@47391 / @49195, cov3-b-e4f@21467 / @23337).** Hit it while it paces
   (2A:B52E), hops at Kirby (2A:B5C0) or hops (2A:B608); stand near a wall so e4f_hop_at reaches it in the air
   (2A:B5E0); be on the side it does not face when e4f_chase starts (2A:B6C9); deal the last hit during its spin in
   the whirl (2A:B9D8).
8. **Last boss's second form (room of main@134756, camera fixed at 0/$C8).** A Star Rod shot fired facing right into
   a reflecting part (29:BD84; the one reflect, cov3-a-wizard@135067, faced left); survive to 10 placements
   (29:B6F0; main has 7); hit his body on the frame his type $61 reaches e61_done (29:B8C6, cov3-c-rodwiz@135476);
   the last hit while a star of a type $61 flies (29:B9EF).
9. **Big Switch (cov5-f-del from @158077).** After a press, leave the switch's room and come back (or replay the
   stage): e6f_done_test frees it (29:BF7D). Enter any switch room with Mike (kirby_ability 6): 29:BFBC.
10. **Runner (type $1C kind $6F, room 67 main@85714, room 194 main@24591).** Stand still on a wide floor so it reaches
   its point three times (2A:BE8D); the third change of side while it is in the air (2A:BEC1, harder).

## Table

| branch | side | target | bytes | unit | routine | verdict | reason |
|---|---|---|---|---|---|---|---|
| 29:A354 | fallthrough | A356 | 11B | en29 | e4a_throw_dir | reachable | no block of shape 2-13 at the nine points ahead ($04 = 0) and random 8 below 4 (answer 3, or 2 when variable 4 is 3). No block happened once (room 137, beetle class 1 facing right, cov4-a-bug7@112741, random was 7). Start: cov4-a-bug7@112741, more grabs facing right; random by grab timing |
| 29:A363 | fallthrough | A365 | 11B | en29 | e4a_throw_dir | reachable | as A354 with random 4-6 (answer 2, or 0 when variable 4 is 2). Same window |
| 29:A375 | fallthrough | A377 | 4B | en29 | e4a_throw_dir | reachable | no block, random 7 and variable 4 = 0 (the previous throw was 0, as the no-block throw of cov4-a-bug7@112741 was): a second no-block grab with random 7 gives throw 3 |
| 29:A451 | taken | A456 | 3B | boss_cov4 | e4a_hover_count | reachable | attack 1 (e4a_fly) of a class 1 beetle ($B7, room 137). e4a_pick rows for obj_param 1: row 3 (kirby_action other) limits 5,5,7 can never give 1; row 4 (action 4/5) gives 1 for random 3-4; row 5 (action $0D) for 0-4. So: Kirby jumping/floating (action 4/5 or $0D, as cov4-a-bugm did for class 0) when e4a_pick runs (not the third pick, which is the summon). Start main@112380 / cov4-a-bug7@112741 |
| 29:A474 | fallthrough | A476 | 3B | boss_cov4 | e4a_fly_pick | reachable | Kirby 32+ px away in X but within 16 px in Y of the hovering beetle when e4a_fly_pick runs (answer 1). Kirby floats at its height. Attack 1 ran in cov4-a-bugm@60717 (room 210) and cov5-g-bug@31765 |
| 29:A49B | fallthrough | A49D | 3B | boss_cov4 | e4a_dive_vel | reachable | e4a_dive_vx is 40 C0 40 C0 by $05*2+$04; the bit-7-clear entries ($40) are the ones with $04 = 0, i.e. the beetle right of Kirby at the dive (entry 1 read: it was left of him). Kirby left of the beetle when e4a_dive starts; cov4-a-bugm@60801 |
| 29:A4CF | taken | A4D7 | 3B | boss_cov4 | e4a_tick_fly | reachable | e4a_hit answers carry only when the hit test changed the beetle without the damage blink (variable 2 still 0): the last hit point / kirby_rect kind 2 (e4a_beaten), as at cov6-j-x@361923 in e4a_tick_bounce. Deal the last hit during the fly or dive (cov4-a-bugm@60717, or a class 1 beetle per A451) |
| 29:A4DF | taken | A4E9 | 3B | en29 | e4a_tick_leap | reachable | as A4CF during e4a_leap (520 ticks in the corpus, w3-sonnet@60345, cov4-a-bug7): the last hit while it leaps |
| 29:A506 | fallthrough | A508 | 10B | boss_cov3 | e4a_tick_bounce | unsure | needs a ceiling hit ($00 bit 1), and obj_collide tests the head only with a negative Y velocity. e4a_tick_drop falls (no rise); e4a_bounce rises only by speed_dir_set's small up speed after a wall. Needs a ceiling within a few px of the beetle's head in an arena; 210 and 137 not checked block by block, 39/124/313 never loaded |
| 29:A522 | taken | A540 | 25B | en29 | e4a_tick_charge | unsure | a landing during the charge (obj_collide set 3, no gravity, Y velocity 0): the foot point must enter a floor, i.e. a slope or step rising under the charge. 3,273 charges in rooms 210 and 137 never did; rooms 39 and 124 (class 1 / 0, never loaded) not checked for slopes |
| 29:A5FA | fallthrough | A5FC | 3B | en29 | e4a_held_step | reachable | Kirby's X crossing 255->256 while he is pulled right (+2 per frame). At the first grab of a fight variable 4 is $FF, the index $FF (+4 or not) reads $33 at 29:A717: target = beetle X + 51. Rooms 210/137 are one screen at X high 0, so the beetle must be at X >= ~207 when it grabs (it faces left, Kirby in front of it). Start cov4-a-bugm@59888 or main@112380 (first grab) |
| 29:A60A | fallthrough | A60C | 3B | en29 | e4a_held_step | unsure | Kirby's X crossing 0 leftward: target = holder X + dx below 0, dx at least -16 (variable 4 = 2 facing right), so the beetle at X < ~16 (or type $4D holding with variable 4 = 0, dx -2: X < 2). In the one-screen rooms 210/137 the walls likely keep it further in; not checked block by block |
| 29:AB6C | fallthrough | AB6E | 4B | boss_cov3 | e4b_throw_kind | reachable | no wall at the six probes (+-$08/$18/$28), random 6-7 and variable 4 = 3 (the previous throw was 3): answer 1. Throw 3 ran in cov5-i-shell; no-wall grabs in cov4-a-turtle@53319 (room 258). A later no-wall grab with random 6-7 |
| 29:AC1A | taken | AC3B | 3B | boss_cov3 | e4b_tick_hang | reachable | as 29:A4CF (e4a_hit with record 6): the last hit point while the shell mid-boss hangs after e4b_leap (attack 3; hang ran from cov3-a-turtle@53926, room 258) |
| 29:AC43 | taken | AC4D | 3B | boss_cov3 | e4b_tick_leaps | reachable | the last hit during e4b_leaps (attack 2; cov3-a-turtle@54116) |
| 29:ACA3 | fallthrough | ACA5 | 3B | boss_cov3 | e4b_tick_spin | reachable | a wall during e4b_spin: X speed grows by $19 every 16 frames toward its facing for 128 frames (~56 px). Grab Kirby with a wall within ~50 px in front of it (cov3-a-turtle@53218 had a wall behind). Room 258 |
| 29:AFB0 | taken | AFC2 | 19B | en29 | e4a_hit | reachable | variable 2 negative after the hit test: record 39:878C (Y = 2, e4a_tick_drop and e4a_tick_bounce) stores $FF for kind 1 of kirby_rect, which is Kirby's slide (hit_rect_k1: flag $40 gives the reaction without damage). Slide into the beetle while it drops in at the start of the fight or bounces off a wall after a charge. Start main@31519 (room 210) or cov3-a-bugzzy@31820 (charge into wall) |
| 29:B6F0 | fallthrough | B6F2 | 5B | en29 | e4e_place | reachable | variable 5 reaching 10 (only e4e_place, obj_spawn and script set_var write it): ten placements in one fight. main has 7 (main@134757). Prolong the fight (fewer hits) |
| 29:B8C6 | fallthrough | B8C8 | 1B | boss_cov3 | e61_done | reachable | the boss's variable 9 not 0 when type $61's script runs e61_done. obj_run steps threads before the tick routine, so if the body is hit (e62_boxes stores 1 in his variable 9) on the frame e61 reaches e61_done (e62 earlier in the list) or the frame before (e62 later), the thread sees it before e61_tick frees the object. Frame-exact; cov3-c-rodwiz@135476, cov4-a-wiz@135532 |
| 29:B9EF | fallthrough | B9F1 | 11B | boss_cov3 | e60_tick | reachable | grandparent's variable 9 = 2: a type $60 star launched by e61_star has variable 2 = the $61's slot, whose variable 2 is the boss; e62_boxes stores 2 there on the last hit (29:BCC4 path, ran 15x). Deal the last hit while such a star flies (attack 1 rounds, cov3-c-rodwiz@135081). To check: the freed $61 slot must not be reused before the star's tick |
| 29:BA20 | taken | BA26 | 60B | boss_cov3 | e60_tick | unsure | variable 6 counts $FF -> 0 (set $FF by e60_aim and e60_launch). Likely unreachable: the speed is $0408/$0400 by obj_vel_polar (one component >= 2.8 px/frame) or larger (launch), the position routine obj_pos_cull frees it outside -16..271 / -16..207, the fight's camera is fixed (cam 0/$C8 throughout main@135000-137000), so a star leaves within ~100 frames unless a wall or floor bursts it first. Not proven: other writers of a star's velocity not checked |
| 29:BB58 | fallthrough | BB5A | 5B | en29 | e62_colors | unsure | the boss's slot no longer type $4E while type $62 lives. In main the fight ends with the room change (e4e_end) while the boss still exists; whether any path frees him first is not checked |
| 29:BCD3 | fallthrough | BCD5 | 1B | en29 | e62_boxes | unreachable | the boss's pose is read at BC3E and again at BCD0; BC41 already returns for a pose >= $80. Between them the only code is obj_pos_copy and, on the body path, hit_test_far with carry clear (carry set jumps away at BC94); a hit test that answers carry clear ran no reaction. Every writer of obj_pose (kd xref 62CF) writes cur_object's slot or the slot obj_spawn just took, never the boss's occupied slot, so the second read equals the first (< $80) and BCD3 always branches |
| 29:BD84 | fallthrough | BD86 | 8B | en29 | e62_reflect | reachable | the reflected shot's new obj_dir has bit 7 set, i.e. the shot faced right before (eor $80). The one reflect (cov3-a-wizard@135067) faced left. Fire a Star Rod shot rightward into a reflecting part of the boss (from his left) |
| 29:BF7D | fallthrough | BF7F | 5B | en29 | e6f_done_test | reachable | the bit of stage_door in $0529 + world is set by e6f_press (29:BFB3, 17x in cov5-f-del from @158077). After the press the room reloads with $05A2 = 1 (e6f_pressed, no done test); leave the switch's room by a door and come back, or replay that stage: e6f_start runs e6f_done_test with the bit set and the switch frees itself |
| 29:BFBC | fallthrough | BFBE | 7B | en29 | e6f_tick | reachable | kirby_ability 6 is Mike (ram-map). Enter any Big Switch room (66 73 85 89 96 107 112 162 202 233 241 254 270 276 296 300 309) holding Mike; with kirby_action $0C (singing) the hit test is skipped too |
| 2A:A0BF | fallthrough | A0C1 | 8B | en2a | e4d_tick_air | unsure | a wall while rising (Y velocity negative) in a state other than 6 and a pose other than $0A/$0B. e4d_jump_up (flame_a, pounce_far, catch) uses pose $0A, e4d_leap is state 6, e4d_hop3 hops straight up (no X velocity). Left: the knock-back of e4d_beaten while it still rises, if its tick is this one ("the thrown type $4D"); the one wall seen that reached A0BC (cov3-b-e4d@114051) had Y velocity 0. Beat it with its back close to a wall to test |
| 2A:A0E8 | fallthrough | A0EA | 3B | en2a | e4d_tick_air | reachable | e4d_burn_run sets variables 5 and 3 = $20 once e4d_away_far answers (Kirby 48+ px behind); obj_vx_slow_a then brakes from $0300, and the script later zeroes the velocity: the next tick finds it 0. In cov3-b-e4d@114050 the dash hit a wall one frame later. Make the burning dash end on open floor (Kirby far from the wall it dashes toward). Room 139, cov3-b-e4d@114014 |
| 2A:A140 | fallthrough | A142 | 13B | en2a | e4d_tick_air | reachable | state 9, pose $3A-$41, variable 6 not 0: a wall during the burning dash sets variable 6 = obj_dir eor $80 (not 0 for $40 or $C0; the dash at 114035-114049 had obj_dir $40 and poses $3A-$40). Stand within ~48 px of the wall it dashes toward, so the wall comes before e4d_away_far. Room 139, cov3-b-e4d@114014 -> state $0A (2A:A5EF, never ran) |
| 2A:A2FF | fallthrough | A301 | 5B | en2a | e4d_next_state | reachable | obj_param 0: kind $BE, rooms 301 (world 5: hub 4 -> 298 -> 304 -> 303 -> 301; main@76370 was in 303 and took the door to 302) and 126 (world 7: room 113's lower door -> 114 ... 125 -> 126; main@111314 took the upper door). Neither room was ever loaded. Its first plan runs this |
| 2A:A497 | fallthrough | A499 | 1B | boss_cov3 | e4d_param_random | reachable | obj_param 0 in e4d_lunge2: class 0 mane (rooms 301 / 126 as A2FF); lunge2 is state 3 at plan step 6 (e4d_plan_states class 0: 4 $0E $0D 6 5 $0E 3 6) or from e4d_random_states (3 for random 6-7) |
| 2A:A801 | taken | A809 | 4B | boss_cov3 | e4d_grip_pose | reachable | kirby_form 1 (mouth full) when a lunge catches Kirby (e4d_hit catches when kirby_form is not 8). Keep something in the mouth (an enemy carried in from room 138, or what the room offers) and get caught. Room 139, cov3-b-e4d@112854 |
| 2A:A807 | fallthrough | A809 | 4B | boss_cov3 | e4d_grip_pose | unreachable | A805 `ldy #$01` right before the `bne` at A807 leaves Z = 0, so the bne always branches; A809 is reached only by the beq at A801 |
| 2A:AB4E | taken | AB67 | 1B | en2a | e49_tick_drop | reachable | a hit (carry) on the wheel's first tick: it lands on that frame every time (173x), so a Kirby hit box or shot must overlap it on the frame it appears. Frame-exact: a shot sent to where it spawns as its column comes into view. Room 176 main@15183, room 164 main@122430 |
| 2A:AB5A | taken | AB67 | 1B | en2a | e49_tick_drop | unsure | no landing on the first frame: a wheel placed above the floor. In rooms 176 and 164 it stands on it; 209 ($B4) and 38 ($B5) never loaded, their placements not checked against the blocks |
| 2A:AC82 | fallthrough | AC84 | 1B | en2a | e49_tick_run | unsure | facing left while rolling away (variable 9 negative) with e49_brake_floor+5[$0C-2] not 0: $0C = 6 (a slope), or $0C = 0/1 (index wraps to code bytes $A9/$20 at 2A:ADA0/ADA1). $0C here is obj_walk's fresh floor class; only flat floors (2) seen in 176/164. The $0C = 0 at w12-sonnet@34363 was e49_brake_step reading a stale $0C before its obj_walk, not a floor. Needs a slope in a wheel arena (209 / 38 not checked) |
| 2A:AD2D | taken | AD35 | 9B | en2a | e49_tick_brake | reachable | variable 6 = $3C at e49_brake and -1 per frame; class 0 brakes $0180 at 7/frame (55 frames), class 1 from $02A0 takes 96 frames. Fight the class 1 wheel ($B5, room 164, main@122420: main left after 2 frames) and let it brake 61+ frames without a wall (Kirby near the wall it rolls away from) |
| 2A:AD75 | fallthrough | AD77 | 5B | en2a | e49_tick_feint | reachable | a wall while the feint rolls away (variable 5 positive): Kirby within 64 px in front of it, one time in three (bit 4 of variable 3, once per stand), with a wall close behind the wheel. Room 176 (feints from w12-opus@26173) or 164 |
| 2A:AE61 | fallthrough | AE63 | 5B | en2a | e49_tick_wheel | reachable | the small wheel meets a wall in the air (before it lands; 288 airborne ticks, 1 landing in the corpus). It flies at Kirby: Kirby standing near a wall when e49_throw throws. Best in the walled one-screen room 164 (class 1); in 176 the wheels seem to leave the screen. Plausible, lifetime of the flicker not checked |
| 2A:AE69 | fallthrough | AE6B | 3B | en2a | e49_tick_wheel | unsure | a ceiling hit by the small wheel in the air: needs an upward speed and a low ceiling in a wheel arena; not checked |
| 2A:AE80 | fallthrough | AE82 | 5B | en2a | e49_tick_wheel | unsure | no floor under the rolling small wheel (a ledge or pit). Needs a ledge in a wheel arena within its rolling life (28 frames of rolling in the one corpus case); 176's arena floor not checked, 164 is one screen |
| 2A:AE89 | fallthrough | AE8B | 5B | en2a | e49_tick_wheel | reachable | a wall while the small wheel rolls: room 164 (one screen, walled; class 1 wheel, main@122420) with Kirby near the wall it rolls toward. Plausible (flicker life not checked) |
| 2A:AEA7 | fallthrough | AEA9 | 3B | en2a | e49_tick_wheel | reachable | the first rolling frame after a landing always sees a floor change (variable 8 = $FF at the landing); the old X velocity negative = rolling left. The one landed wheel rolled right. Kirby left of the big wheel when it throws; room 176 (w12-opus@26468) |
| 2A:AEC2 | fallthrough | AEC4 | 3B | en2a | e49_speed_class | reachable | speed high byte >= 2 at the brake's start: class 1 on a flat floor ($02A0, e49_slope_vx) or class 0 on slope index 2/4. The class 1 wheel in room 164 (main@122420) braking once |
| 2A:AECD | fallthrough | AECF | 1B | en2a | e49_speed_class | unsure | speed $0181-$01FF at the brake's start: only class 1 slope index 1 ($0192) in e49_slope_vx, i.e. a slope in room 164/38 (not checked), unless a feint's partial brake carries over into e49_run (not checked) |
| 2A:AF04 | fallthrough | AF06 | 4B | en2a | e49_brake_step | reachable | a wall while braking. Class 0 (room 176, brake ~41 px after passing Kirby by 64): Kirby 70-100 px from the wall it rolls toward; class 1 (room 164) more room. Also through e49_tick_feint's brakes |
| 2A:B458 | fallthrough | B45A | 5B | en2a | e4f_tick_decide | unsure | Kirby 256+ px away in X at the decision. Impossible in the one-screen rooms 200 and 268 (both X in 0-255). Room 185 is two screens but the camera locks on the fight (cam_x $C0 -> $F2, main@21397-21415), keeping Kirby in view; 116 never loaded; class 1 rooms 129 (no door in) and 316 (demo) |
| 2A:B52E | fallthrough | B530 | 1B | en2a | e4f_tick_pace | reachable | e49_hit returns the hit test's carry: any hit while it paces (e4f_pace starts when Kirby is far after a rest; 682 ticks, w12-sonnet@49195, cov3-b-e4f@22208). A ranged hit (shot, spit star) |
| 2A:B5C0 | fallthrough | B5C2 | 3B | boss_cov3 | e4f_tick_hop_at | reachable | a hit during e4f_hop_at (620 ticks, cov3-b-e4f@23337) |
| 2A:B5E0 | fallthrough | B5E2 | 3B | boss_cov3 | e4f_tick_hop_at | reachable | a wall in the air during e4f_hop_at: X $0100 toward Kirby, Y -$0500, about 45 px forward per hop: stand within ~40 px of a wall so the hop at Kirby reaches it. cov3-b-e4f@23337 |
| 2A:B608 | fallthrough | B60A | 3B | boss_cov3 | e4f_tick_hops | reachable | a hit during e4f_hops (894 ticks, cov3-b-e4f@21467) |
| 2A:B6C9 | fallthrough | B6CB | 8B | en2a | e4f_chase_turn | reachable | obj_face_kirby turning it at the start of e4f_chase: Kirby on the side it does not face when entry $15 begins (cross over it just before). Chase ran 6x, w12-sonnet@47391 (room 185) |
| 2A:B6E1 | fallthrough | B6E3 | 5B | en2a | e4f_tick_chase | unsure | a wall during the chase. It faces Kirby and walks at him; within 32 px in X it spin-slides first. A wall before Kirby needs a step or wall between them with Kirby 32+ px away; flat arenas give none. Not checked for 185 / 116 |
| 2A:B6F0 | taken | B6FD | 5B | en2a | e4f_tick_chase | unsure | reads slot 0's variable 6 ($6236, X = 0 after obj_walk). It is 0 at room start (main@21390) and the first chase tick makes it $FF (w12-sonnet@47391), so taking the beq needs $6236 = 1. Writers: obj_spawn, vm set_var / store_var by slot 0's scripts, fsel_tick, story_fade_pics; none seen to store 1 in play. Likely unreachable, not proven |
| 2A:B6F5 | fallthrough | B6F7 | 5B | en2a | e4f_tick_chase | unsure | on the first chase tick after a room load ($6236 0 -> $FF, not negative before) with Kirby within 32 px in X: entry $12. Depends on how close Kirby can be when entry $15 starts (what leads to the chase not read) |
| 2A:B77D | fallthrough | B77F | 3B | en2a | e4f_tick_slide | unsure | a wall during the spin slide; the slide starts within 32 px of Kirby and loses 8 per frame; reaching a wall past Kirby depends on the chase speed (not read). Plausible with Kirby against a wall |
| 2A:B7A9 | fallthrough | B7AB | 7B | en2a | e4f_tick_slide | unsure | the speed less e4f_slide_steps[class] (8, $0B) going below 0: class 0 speeds are multiples of 8 (288 slide frames, always exact). Class 1 ($0B) is in rooms 129 (no door leads to 127/128) and 316 (demo chain) only. Unsure whether either is playable |
| 2A:B8C9 | fallthrough | B8CB | 3B | en_cov5 | e4f_tick_wall_hop | unsure | a second wall in the air while it bounces back from the first (e4f_wall_bounce): needs a narrow space; not checked |
| 2A:B9D8 | fallthrough | B9DA | 11B | en2a | e4f_free_whirl | reachable | variable 8 holds the whirl's slot during the spin (e4f_tick_wait sets $FF at its end); e4f_tick_spin calls e4f_tick_slide, which runs e49_hit. Deal the last hit with a ranged attack while it spins in the whirl (spins from w12-opus@39403; room 185 main@21393) |
| 2A:BB08 | taken | BB0B | 3B | en2a | e1c_tick_stand | unsure | no floor while it stands (no X speed): the block under it must vanish (a breakable block destroyed) or a placement in the air. 61,265 ticks never; placements of kinds $6B-$6E (rooms 53 58 69 159 179 194 86 147 251 255 273 78 79) not checked against the blocks |
| 2A:BE8D | taken | BE9B | 5B | en2a | e1c_tick_run | reachable | e1c_steer answers variable 6; each stay (variable 5 = $B4 when within 1 px of its point 64 px beside Kirby) gives one change of side 60 frames later. Three stays: Kirby still on a wide flat floor for ~3 x (run + 60) frames. Room 67 (main@85714; changes at main@86257) rather than 194 (pit) |
| 2A:BEC1 | taken | BECF | 51B | en2a | e1c_tick_run_fall | reachable | as BE8D with the runner airborne at its third change: variable 5 counts on in the air, so move Kirby during the third stay so the point is past a ledge and the runner falls off it in the 60 frames. Harder than BE8D |

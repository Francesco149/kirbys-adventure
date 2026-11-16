# Batch 10, slice B (banks 17-22, 1D): verdicts

Row: branch, side never run, its target, bytes, unit, routine. Reachable rows name the movie that runs them, or say 'not made'.

| branch | side | target | bytes | unit | routine | verdict | why / movie |
|---|---|---|---|---|---|---|---|
| 17:A04E | fallthrough | A050 | 5B | kst17 | kirby_st_rod_stand | unreachable | rod states live only in rooms 15/16 (UNUSED.md); room 16's floor (row 23, property $0D) spans the whole width and Kirby's X is held inside kirby_min_x/max_x, so kirby_floor_near always finds it |
| 17:A062 | fallthrough | A064 | 5B | kst17 | kirby_st_rod_stand | unreachable | no ladder (shape 1) in rooms 15/16; script $8B is never read (dead_kirby) |
| 17:A08A | fallthrough | A08C | 5B | kst17 | kirby_st_rod_stand | unreachable | rooms 15/16 have no door tile (kt room: doors []) |
| 17:A09E | fallthrough | A0A0 | 5B | kst17 | kirby_st_rod_stand | unreachable | room 16's floor is one property ($0D) everywhere: floor_kind_index cannot change |
| 17:A0A8 | fallthrough | A0AA | 5B | kst17 | kirby_st_rod_stand | unreachable | the rod's entries set bit 5 of kirby_flags (kst17; $05FB reads $20/$24 in main@134700+), so pad_select_drop answers carry clear |
| 17:A16A | fallthrough | A16C | 5B | kst17 | kirby_st_rod_walk | unreachable | room 16 has no block but the floor row; its sides are kirby_min_x/max_x limits, which kirby_walls (block probes) never reports |
| 17:A174 | fallthrough | A176 | 5B | kst17 | kirby_st_rod_walk | unreachable | rod states live only in rooms 15/16 (UNUSED.md); room 16's floor (row 23, property $0D) spans the whole width and Kirby's X is held inside kirby_min_x/max_x, so kirby_floor_near always finds it |
| 17:A19C | fallthrough | A19E | 5B | kst17 | kirby_st_rod_walk | unreachable | no ladder (shape 1) in rooms 15/16; script $8B is never read (dead_kirby) |
| 17:A1C4 | fallthrough | A1C6 | 5B | kst17 | kirby_st_rod_walk | unreachable | room 16's floor is one property ($0D) everywhere: floor_kind_index cannot change |
| 17:A1CE | fallthrough | A1D0 | 5B | kst17 | kirby_st_rod_walk | unreachable | rooms 15/16 have no door tile (kt room: doors []) |
| 17:A1E2 | fallthrough | A1E4 | 5B | kst17 | kirby_st_rod_walk | unreachable | the rod's entries set bit 5 of kirby_flags (kst17; $05FB reads $20/$24 in main@134700+), so pad_select_drop answers carry clear |
| 17:A21C | fallthrough | A21E | 5B | kst17 | kirby_st_rod_run | unreachable | room 16 has no block but the floor row; its sides are kirby_min_x/max_x limits, which kirby_walls (block probes) never reports |
| 17:A226 | fallthrough | A228 | 5B | kst17 | kirby_st_rod_run | unreachable | rod states live only in rooms 15/16 (UNUSED.md); room 16's floor (row 23, property $0D) spans the whole width and Kirby's X is held inside kirby_min_x/max_x, so kirby_floor_near always finds it |
| 17:A244 | fallthrough | A246 | 5B | kst17 | kirby_st_rod_run | unreachable | no ladder (shape 1) in rooms 15/16; script $8B is never read (dead_kirby) |
| 17:A26C | fallthrough | A26E | 5B | kst17 | kirby_st_rod_run | unreachable | room 16's floor is one property ($0D) everywhere: floor_kind_index cannot change |
| 17:A276 | fallthrough | A278 | 5B | kst17 | kirby_st_rod_run | unreachable | rooms 15/16 have no door tile (kt room: doors []) |
| 17:A28A | fallthrough | A28C | 5B | kst17 | kirby_st_rod_run | unreachable | the rod's entries set bit 5 of kirby_flags (kst17; $05FB reads $20/$24 in main@134700+), so pad_select_drop answers carry clear |
| 17:A2B5 | fallthrough | A2B7 | 5B | kst17 | kirby_st_rod_skid | unreachable | room 16 has no block but the floor row; its sides are kirby_min_x/max_x limits, which kirby_walls (block probes) never reports |
| 17:A2BF | fallthrough | A2C1 | 5B | kst17 | kirby_st_rod_skid | unreachable | rod states live only in rooms 15/16 (UNUSED.md); room 16's floor (row 23, property $0D) spans the whole width and Kirby's X is held inside kirby_min_x/max_x, so kirby_floor_near always finds it |
| 17:A32D | fallthrough | A32F | 5B | kst17 | kirby_st_rod_rise | unreachable | room 16 has no block above the floor row (open to the top), so kirby_ceiling finds nothing |
| 17:A337 | fallthrough | A339 | 5B | kst17 | kirby_st_rod_rise | unreachable | kirby_at_top needs the rod's jump (about 50 px from the floor at y 361) to reach the room's top limit; room 16 is 384 px tall |
| 17:A34B | fallthrough | A34D | 5B | kst17 | kirby_st_rod_rise | unreachable | no ladder (shape 1) in rooms 15/16; script $8B is never read (dead_kirby) |
| 17:A35F | fallthrough | A361 | 5B | kst17 | kirby_st_rod_rise | unreachable | no water in rooms 15/16 (dead_kirby: scripts $8F/$92 never read) |
| 17:A369 | fallthrough | A36B | 5B | kst17 | kirby_st_rod_rise | unreachable | rooms 15/16 have no door tile (kt room: doors []) |
| 17:A39B | taken | A3A5 | 1B | kst17 | rod_spin_rect | unreachable | all 16 bytes of rod_spin_rect_hi are $A3 and the index is the pose rod_spin_pose has just set (- $44) |
| 17:A44C | fallthrough | A44E | 5B | kst17 | kirby_st_rod_fall | unreachable | room 16 has no block above the floor row (open to the top), so kirby_ceiling finds nothing |
| 17:A456 | fallthrough | A458 | 5B | kst17 | kirby_st_rod_fall | unsure | bump_kind >= 0 comes from wall_bump_set (no wall), kirby_ceiling_bump (no ceiling), land_bump_set (the landing leaves for $7C first) or a script's set_mem8; whether a set_mem8 or a landing can leave it >= 0 into a later rod fall was not traced |
| 17:A460 | fallthrough | A462 | 5B | kst17 | kirby_st_rod_fall | unreachable | no ladder (shape 1) in rooms 15/16; script $8B is never read (dead_kirby) |
| 17:A474 | fallthrough | A476 | 5B | kst17 | kirby_st_rod_fall | unreachable | no water in rooms 15/16 (dead_kirby: scripts $8F/$92 never read) |
| 17:A47E | fallthrough | A480 | 5B | kst17 | kirby_st_rod_fall | unreachable | rooms 15/16 have no door tile (kt room: doors []) |
| 17:A492 | fallthrough | A494 | 5B | kst17 | kirby_st_rod_fall | unreachable | the rod's entries set bit 5 of kirby_flags (kst17; $05FB reads $20/$24 in main@134700+), so pad_select_drop answers carry clear |
| 17:A4CF | fallthrough | A4D1 | 5B | cov6_extra | kirby_st_rod_dive | unreachable | room 16 has no block above the floor row (open to the top), so kirby_ceiling finds nothing |
| 17:A4D9 | fallthrough | A4DB | 5B | cov6_extra | kirby_st_rod_dive | unreachable | kirby_flag3 (a block broke under the dive): room 16 has no breakable block (dead_kirby: script $86 never read) |
| 17:A4ED | fallthrough | A4EF | 5B | cov6_extra | kirby_st_rod_dive | unreachable | no ladder (shape 1) in rooms 15/16; script $8B is never read (dead_kirby) |
| 17:A4F7 | fallthrough | A4F9 | 5B | cov6_extra | kirby_st_rod_dive | reachable | cov10-b-roddive (Up held in the rod's dive, 17:A4F9 ran) |
| 17:A501 | fallthrough | A503 | 5B | cov6_extra | kirby_st_rod_dive | unreachable | no water in rooms 15/16 (dead_kirby: scripts $8F/$92 never read) |
| 17:A50B | fallthrough | A50D | 5B | cov6_extra | kirby_st_rod_dive | unreachable | pad_up_held (Up -> inflate) is tested first and pad_up_door also needs Up held; and no door |
| 17:A5EE | fallthrough | A5F0 | 5B | cov7 | kirby_st_rod_bump | unreachable | no water in rooms 15/16 (dead_kirby: scripts $8F/$92 never read) |
| 17:A638 | fallthrough | A63A | 5B | kst_cov3 | kirby_st_rod_duck | unreachable | rod states live only in rooms 15/16 (UNUSED.md); room 16's floor (row 23, property $0D) spans the whole width and Kirby's X is held inside kirby_min_x/max_x, so kirby_floor_near always finds it |
| 17:A64C | fallthrough | A64E | 5B | kst_cov3 | kirby_st_rod_duck | unreachable | down_bit5_test needs a thin floor (bit 5 of prop_shape); none in room 16 (UNUSED.md, dead_kirby script $88) |
| 17:A6A1 | fallthrough | A6A3 | 5B | kst_cov3 | kirby_st_rod_slide | unreachable | room 16 has no block but the floor row; its sides are kirby_min_x/max_x limits, which kirby_walls (block probes) never reports |
| 17:A6AB | fallthrough | A6AD | 5B | kst_cov3 | kirby_st_rod_slide | unreachable | rod states live only in rooms 15/16 (UNUSED.md); room 16's floor (row 23, property $0D) spans the whole width and Kirby's X is held inside kirby_min_x/max_x, so kirby_floor_near always finds it |
| 17:A810 | fallthrough | A812 | 5B | kst17 | kirby_st_rod_swing | unreachable | no water in rooms 15/16 (dead_kirby: scripts $8F/$92 never read) |
| 17:A81A | fallthrough | A81C | 5B | kst17 | kirby_st_rod_swing | unreachable | water_left needs kirby_in_water set; no water with the rod |
| 17:A82A | fallthrough | A82C | 2B | kst17 | rod_swing_gravity | unreachable | kirby_in_water is never set with the rod (no water) |
| 17:A8C0 | fallthrough | A8C2 | 5B | kst17 | kirby_st_rod_inflate | unreachable | rooms 15/16 have no door tile (kt room: doors []) |
| 17:A908 | fallthrough | A90A | 5B | kst17 | kirby_st_rod_flap | unreachable | no water in rooms 15/16 (dead_kirby: scripts $8F/$92 never read) |
| 17:A912 | fallthrough | A914 | 5B | kst17 | kirby_st_rod_flap | unreachable | rooms 15/16 have no door tile (kt room: doors []) |
| 17:A962 | fallthrough | A964 | 5B | kst17 | kirby_st_rod_float | unreachable | no water in rooms 15/16 (dead_kirby: scripts $8F/$92 never read) |
| 17:A96C | fallthrough | A96E | 5B | kst17 | kirby_st_rod_float | unreachable | pad_a_up_held (A or Up -> flap) is tested first and pad_up_door needs Up held; and no door |
| 17:AA0B | fallthrough | AA0D | 5B | kst17 | kirby_st_rod_puff | unreachable | no water in rooms 15/16 (dead_kirby: scripts $8F/$92 never read) |
| 17:AC18 | fallthrough | AC1A | 5B | kst_abl | kirby_st_hammer_stand | reachable | not made: Hammer standing with no floor, as kirby_st_stand did (main@32534: Down off a ladder whose foot is over air, released) and kirby_st_ab_stand (cov5-f-del@197215: an exhale ending in the air) |
| 17:AE82 | fallthrough | AE84 | 5B | kst_cov3 | kirby_st_hammer_skid | reachable | not made: the skid into a wall (kirby_st_sword_turn's same exit ran once) |
| 17:AE8C | fallthrough | AE8E | 5B | kst_cov3 | kirby_st_hammer_skid | reachable | not made: the skid running off a ledge |
| 17:AF01 | fallthrough | AF03 | 5B | kst_abl | kirby_st_hammer_jump_rise | reachable | not made: landing while still in the rise (kirby_st_jump_rise's same exit ran 30x) |
| 17:AF87 | fallthrough | AF89 | 5B | kst_abl | kirby_st_hammer_fall | reachable | not made: the fall with a ceiling (kirby_st_fall 2x, kirby_st_ab_fall 25x took the same exit) |
| 17:AFC3 | fallthrough | AFC5 | 5B | kst_abl | kirby_st_hammer_fall | unreachable | pad_up_held (Up -> inflate) is tested first and pad_up_door also needs Up held (kirby_st_hammer_fall) |
| 17:B00A | fallthrough | B00C | 5B | kst_cov4 | kirby_st_hammer_dive | unsure | kirby_ceiling in the dive needs ceiling_approach's carry: a flat ceiling needs vy < 0 (never in a dive), a sloped one X+Y or Y-X < 0, i.e. |vx| above the dive's fall speed |
| 17:B046 | fallthrough | B048 | 5B | kst_cov4 | kirby_st_hammer_dive | unreachable | pad_up_held (Up -> inflate) is tested first and pad_up_door also needs Up held (kirby_st_hammer_dive) |
| 17:B086 | fallthrough | B088 | 5B | cov5_tour | kirby_st_hammer_dive_hit | unsure | landing while still in the bounce (it leaves by kirby_falling at the top): a bounce onto a slope or ledge |
| 17:B090 | fallthrough | B092 | 5B | cov5_tour | kirby_st_hammer_dive_hit | reachable | not made: a dive bounce under a low ceiling (dive onto an enemy below a ceiling) |
| 17:B0A4 | fallthrough | B0A6 | 5B | cov5_tour | kirby_st_hammer_dive_hit | reachable | cov10-b-hdive (B in the bounce, 17:B0A6 ran) |
| 17:B0AE | fallthrough | B0B0 | 5B | cov5_tour | kirby_st_hammer_dive_hit | reachable | not made: a dive bounce next to a ladder with Up or Down held |
| 17:B0B8 | fallthrough | B0BA | 5B | cov5_tour | kirby_st_hammer_dive_hit | unsure | the bounce rises from a dry dive; water_entered needs water at his point while rising |
| 17:B0C2 | fallthrough | B0C4 | 5B | cov5_tour | kirby_st_hammer_dive_hit | reachable | cov10-b-hdive (Up in the bounce, 17:B0C4 ran) |
| 17:B0CC | fallthrough | B0CE | 5B | cov5_tour | kirby_st_hammer_dive_hit | unreachable | pad_up_held (Up -> inflate) is tested first and pad_up_door also needs Up held (kirby_st_hammer_dive_hit) |
| 17:B0D6 | fallthrough | B0D8 | 5B | cov5_tour | kirby_st_hammer_dive_hit | reachable | cov10-b-hdive (Select in the bounce, 17:B0D8 ran) |
| 17:B123 | fallthrough | B125 | 5B | kst_cov4 | kirby_st_hammer_dive_land | unsure | water_entered in the dive's landing: needs a floor whose point is water while kirby_in_water is 0 (the dive's own water exit comes first) |
| 17:B16D | fallthrough | B16F | 5B | kst_abl | kirby_st_hammer_duck | unsure | a floor that goes away under a ducking Kirby (a breaking block or a moving platform) |
| 17:B269 | fallthrough | B26B | 5B | kst_cov4 | kirby_st_hammer_ladder | reachable | cov10-b-h74 (the ladder's step count wraps to 3 on a long climb, 17:B26B ran) |
| 17:B31F | fallthrough | B321 | 5B | kst_abl | kirby_st_hammer_swing | unsure | the ground swing does not move Kirby unless kirby_air_step finds no floor; water at the swing's point not seen |
| 17:B329 | fallthrough | B32B | 5B | kst_abl | kirby_st_hammer_swing | unsure | needs the ground swing with kirby_in_water set and his point out of the water |
| 17:B42E | taken | B438 | 1B | kst_cov3 | hammer_air_swing_rect | unreachable | all 16 bytes of hammer_air_swing_rects+16 are $B4 |
| 17:B525 | fallthrough | B527 | 5B | kst_cov3 | kirby_st_hammer_flap | reachable | cov10-b-h74 (A one pixel above the sea: the flap's first step enters it, 17:B527 ran) |
| 17:B589 | fallthrough | B58B | 5B | kst_cov3 | kirby_st_hammer_float | unreachable | pad_a_up_held (A or Up -> flap) is tested first and pad_up_door needs Up held |
| 17:B5D1 | fallthrough | B5D3 | 5B | kst_cov5 | kirby_st_hammer_float_water | unsure | puffed on the water; needs his point to leave the water sideways at a pool's edge (the float rests at the surface) |
| 17:B5DB | fallthrough | B5DD | 5B | kst_cov5 | kirby_st_hammer_float_water | unsure | needs a door tile at a water surface |
| 17:B628 | fallthrough | B62A | 5B | kst_cov3 | kirby_st_hammer_puff | reachable | cov10-b-h74 (B ten pixels above the sea: the exhale falls in, 17:B62A ran) |
| 17:B65E | fallthrough | B660 | 5B | cov5_tour | kirby_st_hammer_water_stand | unsure | a floor going away under Kirby standing in water |
| 17:B686 | fallthrough | B688 | 5B | cov5_tour | kirby_st_hammer_water_stand | unsure | needs a door under water |
| 17:B690 | fallthrough | B692 | 5B | cov5_tour | kirby_st_hammer_water_stand | reachable | not made: Select standing on a floor under water with the Hammer |
| 17:B6F7 | fallthrough | B6F9 | 5B | cov5_tour | kirby_st_hammer_water_walk | reachable | not made: walking into a wall under water with the Hammer |
| 17:B729 | fallthrough | B72B | 5B | cov5_tour | kirby_st_hammer_water_walk | unsure | needs a door under water |
| 17:B733 | fallthrough | B735 | 5B | cov5_tour | kirby_st_hammer_water_walk | reachable | not made: walking under water from one floor kind to another (onto a slope) |
| 17:B73D | fallthrough | B73F | 5B | cov5_tour | kirby_st_hammer_water_walk | reachable | not made: walking under water up out of it |
| 17:B7D6 | fallthrough | B7D8 | 5B | kst_cov5 | kirby_st_hammer_swim | reachable | cov10-b-h74 (Select while swimming, 17:B7D8 ran) |
| 17:B85C | fallthrough | B85E | 5B | kst17 | kirby_st_ufo_hover | unreachable | ufo_hover_dir answers carry whenever a direction is held and Up is one; only U+D or U+L+R map to $FF in ufo_pad_dir, and the core drops opposing pairs (tested in kt: UD gives pad1_held_copy 0, ULR gives $08) |
| 17:BC36 | fallthrough | BC38 | 5B | kst17 | kirby_st_rodfly_shot | reachable | cov10-b-rodfly (a shot running when the camera reaches $035D, 17:BC38 ran) |
| 18:A806 | taken | A810 | 6B | frame | stage_mark_done | unsure | stage_kind not 0 (boss stage 7, unit rooms 0-2) when the script runs stage_mark_done; 2,828 calls all had 0; the script that runs it (via 3F:E4DD) was not traced |
| 18:A80E | fallthrough | A810 | 6B | frame | stage_mark_done | unreachable | A = bit_mask[stage_door] | stages_done[world]; bit_mask (3E:CABE) is 01..80, never 0 |
| 18:A888 | fallthrough | A88A | 5B | kst18 | kirby_st_wheel_morph | reachable | not made: Wheel's morph started at the edge of water |
| 18:A8C4 | fallthrough | A8C6 | 5B | kst18 | kirby_st_wheel_roll | unsure | the roll against kirby_min_x/max_x where the limit is not a wall (side_limit_stop) |
| 18:A8EC | fallthrough | A8EE | 5B | kst18 | kirby_st_wheel_roll | reachable | not made: the Wheel rolling into water |
| 18:A96D | fallthrough | A96F | 5B | kst18 | kirby_st_wheel_turn | reachable | not made: the Wheel's turn ending in water |
| 18:A9F5 | fallthrough | A9F7 | 1B | kst18 | wheel_speed_cap | unsure | wheel_speed_cap called with kirby_speed below $0200 (all 5 calls had $0200 or more) |
| 18:AAC5 | fallthrough | AAC7 | 5B | kst18 | kirby_st_tornado | reachable | not made: Tornado spinning into water |
| 18:AC86 | fallthrough | AC88 | 5B | kst18 | kirby_st_fireball_dash | unsure | the dash has vy 0; ceiling_approach needs a sloped ceiling met from the side (kind 7 moving left, kind 8 moving right) |
| 18:AF92 | fallthrough | AF94 | 5B | kst18 | kirby_st_full_stand | unsure | a floor going away under Kirby standing with the mouth full (no ladder or exhale path with the mouth full) |
| 18:AFC4 | fallthrough | AFC6 | 5B | kst18 | kirby_st_full_stand | reachable | not made: Up on a door, standing with the mouth full (no Up test comes before pad_up_door) |
| 18:B181 | fallthrough | B183 | 5B | kst18 | kirby_st_full_skid | reachable | not made: the skid with the mouth full into a wall |
| 18:B20B | fallthrough | B20D | 5B | kst18 | kirby_st_full_rise | reachable | not made: landing in the rise with the mouth full (kirby_st_jump_rise's same exit ran 30x) |
| 18:B233 | fallthrough | B235 | 5B | kst18 | kirby_st_full_rise | reachable | not made: Up held while jumping past a door with the mouth full |
| 18:B30D | fallthrough | B30F | 5B | kst18 | spit_card_clear | unsure | needs hud_card = 9 when spitting; the script that sets card 9 was not found |
| 18:B40F | fallthrough | B411 | 2B | kst18 | swallow_blink_add | unsure | needs kirby_hurt_timer >= $7C at a swallow; hit_kirby sets 1; a set_mem8 (candy?) might set more |
| 18:B4D6 | fallthrough | B4D8 | 5B | kst_cov3 | kirby_st_full_water_stand | unsure | a floor going away under Kirby in water with the mouth full |
| 18:B508 | fallthrough | B50A | 5B | kst_cov3 | kirby_st_full_water_stand | unsure | needs a door under water |
| 18:B573 | fallthrough | B575 | 5B | tail | kirby_st_full_wade | reachable | not made: wading off a ledge in water with the mouth full |
| 18:B5A5 | fallthrough | B5A7 | 5B | tail | kirby_st_full_wade | reachable | not made: wading onto another floor kind (a slope) in water |
| 18:B5AF | fallthrough | B5B1 | 5B | tail | kirby_st_full_wade | unsure | needs a door in water |
| 18:B5B9 | fallthrough | B5BB | 5B | tail | kirby_st_full_wade | reachable | not made: wading out of the water with the mouth full |
| 19:ADF5 | fallthrough | ADF7 | 5B | en19 | goal_seq_step | reachable | not made (very long): only after goal_seq reached 7 (below) and one more goal game |
| 19:AE09 | fallthrough | AE0B | 3B | en19 | goal_seq_step | reachable | not made (very long): 7 goal games in a row whose rows are 0, 1, ... 6 in order |
| 19:AE1B | fallthrough | AE1D | 1B | en19 | goal_seq_full | reachable | not made (very long): as 19:AE09, then the dance |
| 19:B351 | fallthrough | B353 | 5B | kst_cov3 | kirby_st_ball_stand | unsure | a floor going away under the ball at rest |
| 19:B36F | fallthrough | B371 | 5B | kst_cov3 | kirby_st_ball_stand | reachable | cov10-b-ball (Up at the door in ball form, 19:B371 ran) |
| 19:B40E | fallthrough | B410 | 5B | kst_cov3 | kirby_st_ball_roll | reachable | not made: rolling over a door with Up held |
| 19:B47A | fallthrough | B47C | 5B | kst_cov3 | kirby_st_ball_turn | reachable | not made: the ball's turn ending at a wall |
| 19:B484 | fallthrough | B486 | 5B | kst_cov3 | kirby_st_ball_turn | unsure | the ball's turn off a ledge; tried at the right end of the blocks in room 177, the turn stopped on the edge |
| 19:B4F7 | fallthrough | B4F9 | 5B | kst_cov3 | kirby_st_ball_jump_rise | reachable | cov10-b-ball (the jump into the ceiling, 19:B4F9 ran) |
| 19:B501 | fallthrough | B503 | 5B | kst_cov3 | kirby_st_ball_jump_rise | unsure | needs the room's top limit within the ball's jump of a floor |
| 19:B50B | fallthrough | B50D | 5B | kst_cov3 | kirby_st_ball_jump_rise | reachable | not made: Up held while the ball jumps past a door |
| 19:B56A | fallthrough | B56C | 5B | kst_cov3 | kirby_st_ball_air | reachable | cov10-b-ball (A-held bounces grow into the ceiling, 19:B56C ran) |
| 19:B588 | fallthrough | B58A | 5B | kst_cov3 | kirby_st_ball_air | reachable | not made: the ball falling into water |
| 19:B592 | fallthrough | B594 | 5B | kst_cov3 | kirby_st_ball_air | reachable | not made: Up held while the ball is in the air at a door |
| 19:B5C5 | fallthrough | B5C7 | 2B | kst_cov3 | ball_land | unsure | kirby_floor finding a floor while kirby_vy is negative (rising onto a slope) |
| 19:B95B | fallthrough | B95D | 7B | en19 | e05_star_bounds | unsure | extra_state 2 with kirby_min_x's high byte 0 (ran once with it not 0, cov4-b-star) |
| 19:BA5D | fallthrough | BA5F | 1B | en19 | e05_star_vx | unreachable | the negated low byte is 0 only for a low byte of 0; e05_star_vx_lo is $66, $9D, $CC |
| 1D:835C | fallthrough | 835E | 4B | sound | snd_track_cmd | unreachable | the high nibble (0-15) + n with n >= 0 (n < 0 takes the bmi), carry clear before: at most $8E, never a carry |
| 1D:83BC | fallthrough | 83BE | 9B | sound | snd_track_cmd | unreachable | track command $F7 is in no stream (claim cov6_extra.snd.no_unrun_commands) |
| 1D:83DC | fallthrough | 83DE | 38B | sound | snd_track_cmd | unreachable | track command $E2 is in no stream (claim cov6_extra.snd.no_unrun_commands) |
| 1D:8416 | fallthrough | 8418 | 9B | sound | snd_track_cmd | unreachable | track command $E1 is in no stream (claim cov6_extra.snd.no_unrun_commands) |
| 1D:84B2 | taken | 84D5 | 11B | sound | snd_flow | unreachable | flow byte $FE is in no stream (claim cov6_extra.snd.no_unrun_commands) |
| 1D:85B8 | taken | 85E6 | 1B | sound | snd_env_step | unreachable | envelope bytes $A0-$DF: the claim's walk of all 318 envelope elements found only $00-$9F, $F8, $FA-$FD, $FF |
| 1D:85BE | fallthrough | 85C0 | 12B | sound | snd_env_step | unreachable | envelope byte $F0 is in no stream (claim cov6_extra.snd.no_unrun_commands) |
| 21:8FE2 | fallthrough | 8FE4 | 2B | khelp | obj_pose_script | unsure | needs a script whose pose instruction's operand sits at a page start (script_ptr low byte $FF at the inc); not searched |
| 21:90DA | fallthrough | 90DC | 1B | kcoll | kirby_ceiling | unreachable | every path to 21:90D4 passes beq/bmi on probe_dist (1-$7F) and ceiling_approach does not write $0579 |
| 21:97E5 | fallthrough | 97E7 | 5B | kmove | kirby_edge_test | unsure | kirby_move_locked (camera locked): pushed to a limit with a block at the probe point ($0597 = $FF, a crush); plausible in a locked room with blocks at its sides |
| 21:981B | fallthrough | 981D | 6B | kblocks | current_push | unsure | the current pushing X speed to +7 px/frame or more; Kirby's speeds stay far below |
| 21:9825 | fallthrough | 9827 | 10B | kblocks | current_push | unsure | the current pushing X speed to -7 px/frame or less |
| 21:9848 | fallthrough | 984A | 6B | kblocks | current_push | unsure | the current pushing Y speed to +7 px/frame or more |
| 21:9852 | fallthrough | 9854 | 10B | kblocks | current_push | unsure | the current pushing Y speed to -7 px/frame or less |
| 21:9AC5 | fallthrough | 9AC7 | 6B | khelp2 | hook_full_flash2 | unsure | kirby_form not 1 while hook_full_flash2 still runs (21 calls, all form 1) |
| 21:9CCE | fallthrough | 9CD0 | 0B | khelp | kirby_pal_set | unreachable | A = 0 + $9C + carry is never 0 |
| 21:9E79 | fallthrough | 9E7B | 12B | khelp2 | type7_scan | unsure | an object of type 7 (19:B2A0; 3 in attract) in slots 9-17 when Kirby drops or loses an ability |
| 22:8352 | taken | 8357 | 26B | ohelp | obj_water_test_ay | unsure | an enemy in a still tick (obj_water_test, 31 callers) with water 6 px below its point |
| 22:838E | fallthrough | 8390 | 3B | ohelp | obj_water_test2_a | unsure | water found by a caller of obj_water_test2_a that passes a pose (A >= 0); all 104 finds passed $FF |
| 22:83B0 | taken | 83B4 | 20B | ohelp2 | obj_water_test7 | unsure | type $3B or $41 with water 7 px below |
| 22:8738 | fallthrough | 873A | 1B | ohelp3 | obj_dist_to | unsure | a difference whose low byte is 0 (an exact multiple of 256 px, negative) |
| 22:8761 | fallthrough | 8763 | 1B | ohelp3 | obj_dist_to | unsure | a difference whose low byte is 0 (an exact multiple of 256 px) |
| 22:8768 | taken | 8772 | 5B | ohelp3 | obj_dist_to | unsure | a distance of 256 px or more between the two objects |
| 22:87EE | fallthrough | 87F0 | 1B | ohelp3 | obj_dist_pt | unsure | a difference whose low byte is 0 (an exact multiple of 256 px, negative) |
| 22:8813 | fallthrough | 8815 | 1B | ohelp3 | obj_dist_pt | unsure | a difference whose low byte is 0 (an exact multiple of 256 px) |
| 22:881A | taken | 8824 | 5B | ohelp3 | obj_dist_pt | unsure | a distance of 256 px or more to the point |
| 22:8876 | fallthrough | 8878 | 1B | ohelp2 | obj_steer | unreachable | the carry depends only on the caller's table address: the 9 callers pass low bytes $CE $F1 $22 $99 $1B $C4 $BD (and $70 at 29:BA51, never run); none is $F8 or more |
| 22:888A | fallthrough | 888C | 1B | ohelp2 | obj_steer | unreachable | T + 24 carries only for low bytes $E8-$EF; the callers pass $CE $F1 $22 $99 $1B $C4 $BD $70 |
| 22:8ACE | fallthrough | 8AD0 | 4B | ohelp3 | obj_floor_test9 | unsure | obj_floor_test9 called while the object's Y speed is not 0 (51 calls, all 0) |
| 22:8C37 | fallthrough | 8C39 | 2B | ohelp2 | asm_step_back | unsure | a script step for asm_step_back with low byte 0 |
| 22:901C | fallthrough | 901E | 30B | kst_abl | crash_sweep | reachable | not made: Crash used with a parasol carrier (type $2A) in slots 9-17; got Crash by the roulette in main's 2-4 room 185 (stopped at $13), but no carrier came back there; 2-1's beach or 6-4's 'two parasol wielders' with a Crash source would do |
| 22:90A7 | fallthrough | 90A9 | 2B | ohelp2 | asm_vx_var4 | unsure | script_ptr + the operand length carries only when an asm_vx_var4 instruction ends at a page boundary; the scripts were not searched |
| 22:910D | fallthrough | 910F | 2B | ohelp | obj_dx_to | unsure | the other object exactly a multiple of 256 px to the right (the negated low byte 0) |
| 22:9289 | taken | 929F | 17B | ohelp3 | obj_vx_brake | unsure | obj_vx_brake with a negative X speed (e36 braking while moving left) |
| 22:9380 | fallthrough | 9382 | 2B | ohelp3 | asm_vel_dir | unsure | script_ptr carries only when an asm_vel_dir instruction ends at a page boundary; not searched |
| 22:94CF | taken | 94DB | 11B | ohelp3 | obj_keep_in_box | unsure | Kracko's eye above cam_y - $20 (the box's top clamp); not seen in 53,476 calls |
| 22:94D7 | taken | 94DB | 11B | ohelp3 | obj_keep_in_box | unsure | as 22:94CF (same high byte) |
| 22:94D9 | fallthrough | 94DB | 11B | ohelp3 | obj_keep_in_box | unsure | as 22:94CF |
| 22:9528 | taken | 952E | 19B | ohelp3 | obj_keep_in_box | unsure | Kracko's eye left of cam_x - $10 with cam_x 0 (X negative); not seen |
| 22:952A | taken | 9536 | 11B | ohelp3 | obj_keep_in_box | unsure | as 22:9528 |
| 22:952C | fallthrough | 952E | 19B | ohelp3 | obj_keep_in_box | unsure | as 22:9528 |
| 22:95E3 | fallthrough | 95E5 | 2B | ohelp2 | asm_dust | unsure | script_ptr carries only when an asm_dust instruction ends at a page boundary; not searched |
| 22:966D | fallthrough | 966F | 21B | ohelp3 | obj_hurt_blink | unreachable | A = $DA after lda #$DA, the bne is always taken; 22:966F has no static reference |
| 22:969D | taken | 96A2 | 3B | ohelp2 | obj_walk_look | unsure | obj_walk_look: no ground at entry 5 ahead either (obj_shape_ahead carry clear: answer 3) |
| 22:96D1 | fallthrough | 96D3 | 2B | ohelp | asm_anim_start | unsure | script_ptr carries only when an asm_anim_start instruction ends at a page boundary; not searched |
| 22:9700 | fallthrough | 9702 | 19B | ohelp | obj_anim_run | unsure | an animation entry $80-$BF with bits 0-2 clear; the animation tables were not searched |
| 22:9839 | fallthrough | 983B | 8B | ocoll | obj_collide | unsure | an object rising into a ceiling of kind other than 2 (a sloped ceiling, kind 7 or 8) |
| 22:9A2A | taken | 9A30 | 4B | ocoll | obj_down_left | unsure | an object moving down-left pushed out of a slope of kind 8 |
| 22:9A2E | fallthrough | 9A30 | 4B | ocoll | obj_down_left | unsure | the same with kind 7 |
| 22:9AC8 | fallthrough | 9ACA | 4B | ocoll | obj_walk_right_any | unsure | obj_walk_right_any: a hit of a kind other than 2 |
| 22:9CB7 | fallthrough | 9CB9 | 8B | ocoll | obj_hit_left | unsure | obj_hit_left with a kind other than 2/4/6 |
| 22:9EE3 | fallthrough | 9EE5 | 2B | ocoll | obj_floor_approach | unsure | obj_floor_approach: a negative approach number (never in 96,605 calls) |
| 22:9EF8 | fallthrough | 9EFA | 2B | ocoll | obj_floor_approach | unsure | as 22:9EE3 |
| 22:9F1C | fallthrough | 9F1E | 2B | ocoll | obj_floor_approach | unsure | as 22:9EE3 |
| 22:9F39 | fallthrough | 9F3B | 2B | ocoll | obj_floor_approach | unsure | as 22:9EE3 |
| 22:9F5E | taken | 9F64 | 4B | ocoll | obj_floor_approach | unsure | as 22:9EE3 |

Counts: reachable 43, unreachable 69, unsure 71

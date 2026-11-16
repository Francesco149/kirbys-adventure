---
name: cov11-c-mane
start: cov3-b-e4d@114014
reference: forbidden
steps:
  - in room 139 the mane mid-boss (type $4D, slot 11) starts its burning dash (state 9, e4d_burn: tick routine e4d_tick_air 2A:A080) toward the right wall while UFO Kirby rises out of its path: room == 139 and ram[0x6128+11] == 0x4D and ram[0x626C+11] % 16 == 9 and ram[0x6290+11]*256 + ram[0x627E+11] == 0xA080 and y < 140
  - the dash meets the wall while its pose is still one of the dash poses $3A-$41 (variable 6 = its direction eor $80 = $C0), so the state test sends it to state 10 (2A:A142): room == 139 and ram[0x6128+11] == 0x4D and ram[0x626C+11] % 16 == 10 and ram[0x6236+11] == 0xC0 and hp == 23
forbid:
  - lost a life: lives < 6
  - hurt: hp < 23
---
Coverage movie (batch 11, part C; unit en2a / boss_cov3). The mane mid-boss's burning dash (state 9) ran once in the
corpus (cov3-b-e4d), where it caught Kirby and met the wall only after e4d_away_far had set pose $42, so
e4d_tick_air's state-9 test never found variable 6 set during a dash pose (2A:A140 always taken). Here UFO Kirby flies
straight up from X 178, out of the dash, and stays within ~50 px of the right wall: the dash reaches the wall at pose
$40, obj_collide's wall exit stores variable 6 = $C0, and the next state test takes state 10 (2A:A142-2A:A14C,
e4d_set_state). The slow-down to 0 on open floor (2A:A0E8) and the grip with something in the mouth (2A:A801) stay
open: the dash happens once per fight and UFO Kirby cannot inhale.

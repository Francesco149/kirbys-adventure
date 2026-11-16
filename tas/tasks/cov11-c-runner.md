---
name: cov11-c-runner
start: main@35974
reference: forbidden
steps:
  - in room 220 Kirby stands still on the floor in the middle of the room (both of the runner's points, Kirby's X -64 and +64, lie on its platform) while the runner (type $1C, slot 14) runs on e1c_tick_run: room == 220 and abs(x - 129) <= 2 and ram[0x6128+14] == 0x1C and ram[0x6290+14]*256 + ram[0x627E+14] == 0xBE6F
  - the runner has stayed at its point and changed side twice (variable 6 = 2): room == 220 and ram[0x6128+14] == 0x1C and ram[0x6236+14] == 2
  - the third change of side (variable 6 = 3) makes e1c_tick_run start entry $0B of e1c_scripts (2A:BE9B), whose tick routine is e1c_tick_hit (2A:BED4): room == 220 and ram[0x6128+14] == 0x1C and ram[0x6236+14] == 3 and ram[0x6290+14]*256 + ram[0x627E+14] == 0xBED4
forbid:
  - lost a life: lives < 4
---
Coverage movie (batch 11, part C; unit en2a). The runner (type $1C) runs to a point 64 px beside Kirby, stays there
(variable 5 = $B4) and changes side 60 frames later (e1c_steer: variable 3 flips, variable 6 + 1). No movie ever let it
make three changes, so e1c_tick_run's test of the answer 3 (2A:BE8D) never branched. Room 220 is one screen with a
platform across the whole width: Kirby walks to X 129 and stands still under it; the runner goes 65 -> 193 -> 65 ->
193, and at its third change it starts entry $0B (2A:BE9B, e1c_set_script) and e1c_tick_hit (2A:BED4) runs: it jumps
off the top of the screen. The airborne variant (2A:BEC1, entry $0C) needs the third change while the runner falls,
which this platform does not allow.

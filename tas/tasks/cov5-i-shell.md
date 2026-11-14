---
name: cov5-i-shell
start: main@111880
reference: forbidden
steps:
  - in 7-2's room 135 Select drops main's UFO, the shell mid-boss (type $4B) in slot 11: room == 135 and ram[0x5E0] == 0 and ram[0x6128+11] == 0x4B
  - it rolls at Kirby (X velocity -$0540) and grabs him from the roll: room == 135 and ram[0x50C] == 1 and ram[0x7AA] == 11 and ram[0x60F2+11] == 0xFA and hp == 31
  - after the throw it grabs Kirby again near the left wall, facing left, and the throw kind it picks equals the last one, so variable 4 becomes 0: room == 135 and ram[0x50C] == 1 and ram[0x7AA] == 11 and ram[0x6212+11] == 0 and hp == 23
  - a third grab in the middle of the room, no wall within $28 pixels, picks the kind by a random number of 6 or 7 (variable 4 = 3): room == 135 and ram[0x50C] == 1 and ram[0x6212+11] == 3 and ram[0x6086+11]*256 + ram[0x6074+11] >= 60 and ram[0x6086+11]*256 + ram[0x6074+11] <= 196 and hp == 15
forbid:
  - lost a life: lives < 6
  - dying: hp > 47
---
Coverage movie (cov5, unit en29 / boss_cov3). From main in 7-2's room 135 (the shell mid-boss, type $4B) Select drops
the UFO; main's UFO Kirby was never grabbed. The normal-form Kirby stands in the way of its roll: e4a_grab_test
answers carry set inside e4b_tick_roll (29:AC73-AC86: hit_kirby_off, e4a_holder, the script 29:A895). It throws him
three times (31 -> 23 -> 15 -> 7 hit points): the first and second grab near the left wall facing left, so
e4b_throw_kind's wall bits answer kind 3 both times and the second time 0 (29:AB7A); the third in the middle, no point
meets a wall and the random number is 6 or 7 (29:AB58-AB5A, 29:AB67-AB6C: kind 3). On the way e4a_held_tick's
path 29:B0AA-B0AF runs.

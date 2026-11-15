---
name: cov9-b-ddd
start: cov4-a-ddd@131400
reference: forbidden
steps:
  - King Dedede (type $47, slot 10) carries his hammer (tick e47_tick_carry 2D:A6EF) in the 7-7 ring: room == 14 and ram[0x6128+10] == 71 and ram[0x629A]*256 + ram[0x6288] == 0xA6EF
  - Kirby floats high (his Y less than cam_y + $60 by the low bytes) when the boss comes near: e47_hammer_pick picks swing 2 and the boss runs e47_swing_2 (tick e47_tick_swing2 2D:A7D4): room == 14 and ram[0x629A]*256 + ram[0x6288] == 0xA7D4 and ram[0x6212+10] == 2
  - the high leap ends and the boss thinks again (tick e47_tick_think or another action): room == 14 and ram[0x6128+10] == 71 and ram[0x629A]*256 + ram[0x6288] not in (0xA7D4, 0xD786)
  - later the boss flies (e47_fly, tick e47_tick_fly 2D:AA64) at full hit points: room == 14 and ram[0x629A]*256 + ram[0x6288] == 0xAA64 and ram[0x61D4] == 100
  - Kirby's puff of air hits him in the flight: the flight's record 39:8A2C, reaction $0C e47_flight_hurt: room == 14 and ram[0x61D4] < 100
forbid:
  - lost a life: lives < 7
---
Coverage movie (cov9, unit dead_en2 / en2d). From cov4-a-ddd at the start of the 7-7 fight, Kirby floats above the
ground while King Dedede walks at him with the hammer: e47_hammer_pick finds cam_y - Kirby's Y (low bytes) $A0 or
more and picks swing kind 2, so the boss runs e47_swing_2 (the high leap e47_big_jump / e47_big_fall, tick
e47_tick_swing2) and the hammer e63_swing_2_rest (tick e63_tick_swing2). Later he flies (e47_fly), and a puff of air
Kirby exhales hits him during the rise: the damage reaction of the flight's record 39:8A2C, e47_flight_hurt.

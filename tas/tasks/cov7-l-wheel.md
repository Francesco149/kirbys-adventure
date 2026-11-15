---
name: cov7-l-wheel
start: main@17270
reference: forbidden
steps:
  - Wheel Kirby standing on the block beside the left pool of room 179: room == 179 and ability == 7 and x >= 72 and x <= 100 and y >= 80 and y <= 95 and vy == 0
  - the wheel over the pool (kirby_st_wheel_air or another wheel routine): room == 179 and ability == 7 and ram[0x6291]*256 + ram[0x627F] in (0xA8AB, 0xA980, 0xA949, 0xA882) and x < 66 and y >= 104
  - in the water with the Wheel: room == 179 and ability == 7 and ram[0x05F7] != 0
  - the Wheel dropped with Select: room == 179 and ability == 255 and frame > 17460
  - normal Kirby standing at the foot of the ladder: room == 179 and ability == 255 and abs(x - 168) <= 4 and ram[0x6291]*256 + ram[0x627F] == 0xA79B
  - jumping (kirby_st_jump_rise): room == 179 and ability == 255 and ram[0x6291]*256 + ram[0x627F] == 0xAA5C
  - Up held in the rise takes the ladder: room == 179 and ability == 255 and ram[0x6291]*256 + ram[0x627F] == 0xAD96
forbid:
  - lost a life: lives < 4
---
Coverage movie (unit kst18). From main in World 2's room 179 with the Wheel (copied in room 176): Kirby lands on the
block beside the left pool, becomes the wheel and leaves the block, and the wheel falls into the pool:
kirby_st_wheel_air's water_entered exit (18:A9C3, script $33). Then the Wheel is dropped with Select and normal
Kirby, at the foot of the ladder, presses A and holds Up from the rise of the jump: kirby_st_jump_rise has no Up test
before kirby_ladder_test, so its ladder exit (14:AAA0, script $11) is taken.

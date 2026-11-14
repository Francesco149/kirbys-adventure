---
name: cov4-c-ab
start: main@17300
reference: forbidden
steps:
  - Wheel Kirby (form 2) on the ladder of 2-3's cave: room == 179 and ability == 7 and ram[0x6291]*256 + ram[0x627F] == 0xBA71
  - the dive into the left pool: room == 179 and ability == 7 and ram[0x6291]*256 + ram[0x627F] == 0xBE07 and x < 60
  - puffed up on the water with the ability: room == 179 and ability == 7 and ram[0x6291]*256 + ram[0x627F] == 0xBC23
  - the Wheel dropped with Select while swimming: room == 179 and ability == 255 and frame > 18390
  - plain Kirby puffed up on the water: room == 179 and ability == 255 and ram[0x6291]*256 + ram[0x627F] == 0xAF48
forbid:
  - lost a life: lives < 4
---
Coverage movie for the exits of the shared ability states (kirby_form 2, bank 14, units kst14b and kst_abl) and a
few of plain Kirby's, in 2-3's cave (room 179) with main's Wheel: the ladder from the rise, a walk and the dive
(beside the ladder), the dive into the pool, a stroke while walking under water, the float coming down on the
water, Select while swimming; then without the ability the float coming down on the water and B there.

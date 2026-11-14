---
name: cov5-h-hammer
start: cov4-c-hammer@92325
reference: forbidden
steps:
  - B in the Hammer's dive, the swing in the air: room == 75 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB3E5 and frame < 92340
  - a second dive: room == 75 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xAFE5 and frame > 92400
  - Up held in it, puffed up: room == 75 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB4BD and frame > 92400
  - on the shore of 6-3 with the Hammer: room == 74 and ability == 8
  - falling into the sea (kirby_st_hammer_fall, then the water states of bank 17): room == 74 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB789
  - swinging in the air just above the sea: room == 74 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB3E5 and y >= 150
  - puffed up and floating down onto the sea: room == 74 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB5A7
  - exhaling just above the sea: room == 74 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB608 and y >= 150
forbid:
  - lost a life: lives < 6
---
Coverage movie for the Hammer's states (units kst_cov4, kst_abl, kst_cov3) in 6-3 from cov4-c-hammer: in the ship's
room 75 B (script $A8) and Up held (script $A9) during kirby_st_hammer_dive; then on the shore (room 74) Kirby enters
the sea from kirby_st_hammer_fall, kirby_st_hammer_air_swing, kirby_st_hammer_float (puffed, into the float on the
water) and the exhale: the water_entered exits of those states and the Hammer's water states that follow.

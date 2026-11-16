---
name: cov10-a-pool
start: cov7-l-pool@4100
reference: forbidden
steps:
  - Beam Kirby spits water under the pool's surface (kirby_st_ab_water_spit): room == 45 and ability == 15 and ram[0x6291]*256 + ram[0x627F] == 0xBF0D and ram[0x05F7] != 0
  - the spit carries him out of the water (kirby_in_water cleared): room == 45 and ability == 15 and ram[0x05F7] == 0 and frame < 4150
  - floating with the Beam a pixel above the surface, A pressed (the flap, kirby_st_ab_flap): room == 45 and ability == 15 and ram[0x6291]*256 + ram[0x627F] == 0xBBC7 and y == 126 and ram[0x05F7] == 0
  - the flap takes him into the water still full of air (script $30, kirby_st_ab_float_water) without a frame of the float in between: room == 45 and ability == 15 and ram[0x6291]*256 + ram[0x627F] == 0xBC23 and frame < 4280
  - floating over the pool again: room == 45 and ability == 15 and ram[0x6291]*256 + ram[0x627F] == 0xBBC7 and y < 128
  - B lets the air out (kirby_st_ab_puff) above the surface: room == 45 and ability == 15 and ram[0x6291]*256 + ram[0x627F] == 0xBC84 and ram[0x05F7] == 0
  - and the puff state ends in the water: room == 45 and ability == 15 and ram[0x05F7] != 0 and frame > 4330
  - knocked back (kirby_st_hurt) just above the surface, the Beam lost: room == 45 and ability == 255 and hp == 39 and ram[0x6291]*256 + ram[0x627F] == 0xA24A and ram[0x05F7] == 0 and y >= 121
  - the knock-back ends in the water: room == 45 and hp == 39 and ram[0x05F7] != 0
forbid:
  - lost a life: lives < 4
---
Coverage movie (cov10, units kst14b and dead_kirby). World 1's pool (room 45) with the Beam from cov7-l-pool: the
water spit under the surface carries Kirby out of the water (kirby_st_ab_water_spit's water_left exit 14:BF13,
script $39); a flap a few pixels above the surface ends in the water (kirby_st_ab_flap's water_entered exit 14:BBA1,
script $30); B while floating low over the pool lets the air out and the puff state falls into the water
(kirby_st_ab_puff's water_entered exit 14:BCA4, script $33). Then a hit from the Bronto Burt a few pixels above the
surface: the knock-back (kirby_st_hurt) falls into the water before its 13 frames are over, the exit 14:A262 and
script $EB (kirby_s_hurt_water, 14:A240: the splash, then kirby_s_hurt_end), which no movie had run.

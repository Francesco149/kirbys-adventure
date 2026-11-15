---
name: cov7-l-pool
start: cov2-abilities-beam@4080
reference: forbidden
steps:
  - Beam Kirby walks into the pool's right wall under water (kirby_st_ab_water_walk -> stand): room == 45 and ability == 15 and x >= 584 and ram[0x6291]*256 + ram[0x627F] == 0xBCCE
  - Select while walking under water drops the Beam: room == 45 and ability == 255 and y >= 150 and frame < 4260
  - a mouthful taken above the pool: room == 45 and mouth != 255
  - wading on the pool floor with the mouth full (kirby_st_full_wade): room == 45 and mouth != 255 and ram[0x6291]*256 + ram[0x627F] == 0xB54D
  - swallowed under water, then Select standing in the water drops the new ability: room == 45 and ability == 255 and y >= 150 and frame > 4790
  - two things inhaled at once above the pool (the large star): room == 45 and ram[0x05E0] == 1 and ((ram[0x05E6] >> 4) + (ram[0x05E6] & 15)) >= 2
  - the large star spat under water: room == 45 and ram[0x05E0] == 0 and y >= 150 and frame > 5100
  - the inhale ended in the air over the pool (kirby_st_inhale_stop): room == 45 and ram[0x6291]*256 + ram[0x627F] == 0xAED1 and x > 475 and x < 575 and y > 95 and y < 125
  - and Kirby falls from it into the water: room == 45 and y >= 140 and frame > 5432
forbid:
  - hurt: hp < 47
---
Coverage movie (units kst_abl, kst14b, tail). World 1's pool (room 45) with the Beam from cov2-abilities-beam: under
water kirby_st_ab_water_walk's wall exit (14:BD77) and Select exit (14:BDC7); normal Kirby walking into the same wall
(kirby_st_water_walk 14:B0A0); a mouthful taken above the pool, the wade on the pool floor stopping
(kirby_st_full_wade's kirby_speed_zero exit 18:B57F); swallowed under water, and Select in
kirby_st_ab_water_stand (14:BD11). Last, two things are inhaled at once and spat under water: the large star starts in water
(kfx_shot_big_tick 16:B4A1, the script at 16:B492 and what follows). Then Kirby
inhales in the air above the pool and the inhale's end state falls into the water (kirby_st_inhale_stop's water_entered
exit, 18:AED9).

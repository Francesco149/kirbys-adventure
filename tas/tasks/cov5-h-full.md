---
name: cov5-h-full
start: cov3-c-wade@13297
reference: forbidden
steps:
  - standing in the pond with the mouth full: room == 45 and ram[0x5E0] == 1 and ram[0x6291]*256 + ram[0x627F] == 0xB4C7
  - Down there, swallowed under water: room == 45 and ram[0x6291]*256 + ram[0x627F] == 0xB3E7 and frame < 13340
  - full again and standing in the pond: room == 45 and ram[0x5E0] == 1 and ram[0x6291]*256 + ram[0x627F] == 0xB4C7 and frame > 13700
  - B there, spat out under water: room == 45 and ram[0x6291]*256 + ram[0x627F] == 0xB2DF and frame > 13700
  - full and standing in the pond a third time: room == 45 and ram[0x5E0] == 1 and ram[0x6291]*256 + ram[0x627F] == 0xB4C7 and frame > 13870
  - A there, the stroke: room == 45 and ram[0x5E0] == 1 and ram[0x6291]*256 + ram[0x627F] == 0xB5F3 and frame > 13870
  - a skid with the mouth full on land: room == 45 and ram[0x5E0] == 1 and ram[0x6291]*256 + ram[0x627F] == 0xB178
  - Down in the skid, swallowed: room == 45 and ram[0x6291]*256 + ram[0x627F] == 0xB3E7 and frame > 14300
  - plain Kirby in the pond, spitting with B while Up is held, then Down (kirby_spit_dir 4 and 5): room == 45 and ram[0x6291]*256 + ram[0x627F] == 0xB222 and frame > 14500
  - B held on and the direction changed during the spit (kirby_st_water_spit_2): room == 45 and ram[0x6291]*256 + ram[0x627F] == 0xB218 and frame > 14700
forbid:
  - lost a life: lives < 4
---
Coverage movie for Kirby with his mouth full (unit kst_cov3, kst18; bank 18), in 1-1's last area (room 45) from
cov3-c-wade: standing under water in the pond (kirby_st_full_water_stand) he swallows with Down (script $59), spits
with B ($58) and strokes with A ($5D, swim_stroke_test); on land he runs, skids (kirby_st_full_skid) and swallows
there with Down held ($59). Last, without a mouthful, back in the pond: water spits with Up and with Down held
(kirby_spit_dir answers 4 and 5), and B held while the direction changes to Up and to Down
(kirby_spit_dir_test in kirby_st_water_spit_2).

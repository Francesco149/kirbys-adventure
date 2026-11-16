---
name: cov10-a-sword
start: main@64640
reference: forbidden
steps:
  - Sword Kirby wading on the floor of 5-2's flooded tunnel (room 23, kirby_st_sword_wade) up to the step down at x 672: room == 23 and ability == 3 and ram[0x6291]*256 + ram[0x627F] == 0xAAF7 and x >= 650 and y == 153
  - he walks off the step and swims (script $7A, kirby_st_sword_swim) in the deeper water: room == 23 and ability == 3 and ram[0x6291]*256 + ram[0x627F] == 0xABA5 and x > 672 and y > 153
  - above the deep pool on the right, a slash in the air (kirby_st_sword_slash) a few pixels over the surface: room == 23 and ability == 3 and ram[0x6291]*256 + ram[0x627F] == 0xA753 and ram[0x05F7] == 0 and x >= 850 and y >= 52
  - the slash falls into the pool (script $77, then swimming): room == 23 and ability == 3 and ram[0x05F7] != 0 and x >= 850 and y < 80
forbid:
  - hurt: hp < 47
---
Coverage movie (cov10, units kst15 and kst_rest). From main just after the Sword is copied in 5-2's flooded tunnel
(room 23): Sword Kirby wades right along the tunnel's floor and walks off the step where the floor drops at x 672,
kirby_st_sword_wade's kirby_floor_near exit (15:AB1D, script $7A: he swims). Then out of the tunnel by the ladder and
over the wall to the deep pool on the right: a slash in the air a few pixels above the surface falls into the water,
kirby_st_sword_slash's water_entered exit (15:A759, script $77).

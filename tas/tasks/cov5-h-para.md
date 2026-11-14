---
name: cov5-h-para
start: cov4-c-para@24383
reference: forbidden
steps:
  - Parasol Kirby floating on the water of 2-3's room 181: room == 181 and ability == 9 and ram[0x6291]*256 + ram[0x627F] == 0xB55F
  - B there, into the water: room == 181 and ability == 9 and ram[0x6291]*256 + ram[0x627F] == 0xB5C3
  - out again, floating under the open parasol: room == 181 and ability == 9 and ram[0x6291]*256 + ram[0x627F] == 0xB068
  - Select there, the Parasol dropped: room == 181 and ability == 255
forbid:
  - lost a life: lives < 3
---
Coverage movie for two pad exits of Parasol Kirby (bank 15, units kst_cov4 and kst15) in 2-3's room 181 from
cov4-c-para: B new while floating on the water (kirby_st_para_float_water, 15:B581) and Select while floating down
under the parasol (kirby_st_para_float, pad_select_drop, 15:B0CE).

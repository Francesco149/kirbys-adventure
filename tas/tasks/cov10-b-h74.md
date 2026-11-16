---
name: cov10-b-h74
start: cov5-h-hammer@93860
reference: forbidden
steps:
  - Hammer Kirby on the ladder by the pillar of 6-3's shore (room 74; kirby_st_hammer_ladder, 17:B23E): room == 74 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB23E
  - Up held to the fifth step of the climb: the step count (variable 3, $6201) runs below 0 and starts again at 3: room == 74 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB23E and ram[0x6201] == 3 and y < 98
  - puffed up and floating down over the sea: room == 74 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB54B and y >= 150 and frame > 94100
  - A one pixel above the water: the flap's first step takes him in (kirby_st_hammer_flap's water_entered, script $AB), floating on the water: room == 74 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB5A7 and frame <= 94125
  - out of the sea and puffed up again above it: room == 74 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB54B and frame > 94210
  - B ten pixels above the water: the exhale (kirby_st_hammer_puff) falls into it (water_entered, script $AE) and he swims: room == 74 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB789 and frame > 94285
  - Select while swimming drops the Hammer (kirby_st_hammer_swim's pad_select_drop): room == 74 and ability == 255
forbid:
  - lost a life: lives < 6
---
Coverage movie (cov10, units kst_cov4, kst_cov3, kst_cov5): Hammer Kirby on 6-3's shore and sea (room 74), from
cov5-h-hammer@93860. He climbs the pillar's ladder with Up held long enough that the climb's step count runs out and is
set to 3 again (17:B269 falls through). Puffed up over the sea, A when he is one pixel above the water: the flap's
first step (kirby_st_hammer_flap) takes him in (17:B525). He swims up and out, puffs up, and exhales ten pixels above
the water: the puff (kirby_st_hammer_puff) falls in (17:B628). Swimming, Select drops the Hammer (17:B7D6).

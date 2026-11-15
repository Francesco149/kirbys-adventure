---
name: cov7-l-hwater
start: cov5-f-del@236560
reference: forbidden
steps:
  - Hammer Kirby standing on the blocks under water in 5-6's switch room (kirby_st_hammer_water_stand): room == 52 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB64F and frame < 236600
  - walking there (kirby_st_hammer_water_walk): room == 52 and ability == 8 and ram[0x6291]*256 + ram[0x627F] == 0xB6DB and frame > 236600
  - Select while walking drops the Hammer: room == 52 and ability == 255 and y < 100
forbid:
  - lost a life: lives < 4
---
Coverage movie (unit cov5_tour). From cov5-f-del in 5-6's switch room (room 308), where Hammer Kirby stands on the
blocks under water: A held in kirby_st_hammer_water_stand (the swim_stroke_test exit, 17:B674), A held while walking
(17:B721) and Select while walking (pad_select_drop, 17:B749). The water there ends in a pit below the blocks and has
no wall at the block tops, so the wall, floor-kind and water_left exits stay out of reach in this room; the ability
star dropped under water cannot be inhaled again, so the standing Select (17:B692) is left.

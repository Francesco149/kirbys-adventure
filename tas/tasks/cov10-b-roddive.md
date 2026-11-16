---
name: cov10-b-roddive
start: main@135100
reference: forbidden
steps:
  - puffed up with the Star Rod in the last fight (room 16; kirby_st_rod_inflate / float): room == 16 and ability == 24 and y < 300
  - after 28 frames of falling the Star Rod's dive (kirby_st_rod_dive, 17:A4AA), well above the floor: room == 16 and ability == 24 and ram[0x6291]*256 + ram[0x627F] == 0xA4AA and y < 330
  - Up held in the dive: script $8D, puffed up again (kirby_st_rod_inflate, 17:A8A2) before reaching the floor: room == 16 and ability == 24 and ram[0x6291]*256 + ram[0x627F] == 0xA8A2 and y > 330 and y < 350
forbid:
  - hurt: hp < 39
---
Coverage movie (cov10, unit cov6_extra): the Up exit of kirby_st_rod_dive (17:A4F7), the one exit of the Star Rod's
dive that room 16 allows (it has no ladder, water, door, ceiling or breakable block; the rod's states are held only in
rooms 15 and 16). From main@135100 Kirby floats up with the rod, exhales, falls for 28 frames into the dive
(cov6-j-x had it once and left it by B and by landing), and holds Up in it: pad_up_held answers carry and script $8D
puffs him up again in the air.

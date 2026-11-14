---
name: cov5-h-abdive
start: cycle-sub-fable@1346
reference: forbidden
steps:
  - the bounce after a dive onto an enemy, with the ability: room == 43 and ability == 15 and ram[0x6291]*256 + ram[0x627F] == 0xB8B2
  - Up held in it, puffed up with the ability: room == 43 and ability == 15 and ram[0x6291]*256 + ram[0x627F] == 0xBB3B
  - a second bounce with the ability: room == 43 and ability == 15 and ram[0x6291]*256 + ram[0x627F] == 0xB8B2 and frame > 1600
  - Select in it, the ability dropped: room == 43 and ability == 255 and frame > 1600
  - the bounce without an ability: room == 43 and ability == 255 and ram[0x6291]*256 + ram[0x627F] == 0xABE1
  - Up held in it, puffed up: room == 43 and ability == 255 and ram[0x6291]*256 + ram[0x627F] == 0xAE60
  - a second bounce without an ability: room == 43 and ability == 255 and ram[0x6291]*256 + ram[0x627F] == 0xABE1 and frame > 2000
  - B in it, inhaling: room == 43 and ability == 255 and ram[0x6291]*256 + ram[0x627F] == 0xACF6 and frame > 2000
forbid:
  - lost a life: lives < 4
---
Coverage movie for the pad exits of the bounce after a dive hits an enemy (units kst14 and kst14b), in 1-1's room
43 from cycle-sub-fable (Kirby with ability $0F): kirby_st_ab_dive_hit with Up held (script $2E) and with Select
(pad_select_drop, script $01); then plain Kirby's kirby_st_dive_hit with Up held (script $12) and with B (pad_b_new,
script $4B). The dives come from falls of about 30 frames onto Waddle Dees.

---
name: cov5-h-rod
start: main:8-wizard-fight
reference: forbidden
steps:
  - falling with the Star Rod after an exhale (kirby_st_rod_fall): room == 16 and ability == 24 and ram[0x6291]*256 + ram[0x627F] == 0xA428
  - Up held in the fall, puffed up again: room == 16 and ability == 24 and ram[0x6291]*256 + ram[0x627F] == 0xA8A2 and frame > 135300
forbid:
  - lost a life: lives < 8
---
Coverage movie for kirby_st_rod_fall's Up exit (unit kst17, 17:A48A, script $8D) in Nightmare's wizard fight (room
16): Kirby puffs up with the Star Rod, exhales, and when the exhale's fall turns into kirby_st_rod_fall he holds Up
and puffs up again.

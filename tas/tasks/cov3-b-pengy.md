---
name: cov3-b-pengy
start: main@31420
reference: forbidden
steps:
  - Pengy (type $3A) is in slot 12 of room 208: room == 208 and ram[0x6134] == 0x3A
  - it blows (variable 4 = 3): ram[0x6134] == 0x3A and ram[0x621E] == 3
  - it lives through the whole breath and its script reaches 26.B319: ram[0x6134] == 0x3A and ram[0x63A0 + ram[0x6158]]*256 + ram[0x6380 + ram[0x6158]] >= 0xB319 and ram[0x63A0 + ram[0x6158]]*256 + ram[0x6380 + ram[0x6158]] < 0xB327
forbid:
  - lost a life: lives < 4
---
Coverage movie (unit en26b). In room 208 Kirby lets Pengy blow its 24 pieces of breath and keeps out of them
without hurting it, so the script after the breath loop (26:B319) and the wait of variable 6 in e3a_tick (26:B3C0)
run; no Pengy of the corpus lived through its breath.

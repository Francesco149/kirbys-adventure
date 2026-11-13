---
name: cov3-b-e4f
start: main@21340
reference: forbidden
steps:
  - the mid-boss of type $4F is in slot 11 of room 185 and UFO Kirby is there: room == 185 and ram[0x6133] == 0x4F and ability == 23
  - it begins a decision with Kirby 72 pixels or more above it (row 2 of e4f_choices): ram[0x6133] == 0x4F and (ram[0x629B]*256 + ram[0x6289]) == 0xB448 and (ram[0x60B5]*256 + ram[0x60A3]) - y >= 72
  - it begins a decision with Kirby 136 pixels or more away in X (rows 0 and 1): ram[0x6133] == 0x4F and (ram[0x629B]*256 + ram[0x6289]) == 0xB448 and abs(x - (ram[0x6091]*256 + ram[0x607F])) >= 136
  - its script runs entry 0x0B of e49_scripts (2A.B0E4): ram[0x6133] == 0x4F and (ram[0x63A0 + ram[0x6157]]*256 + ram[0x6380 + ram[0x6157]]) >= 0xB0E4 and (ram[0x63A0 + ram[0x6157]]*256 + ram[0x6380 + ram[0x6157]]) < 0xB0F1
  - its script runs 2A.B12B: ram[0x6133] == 0x4F and (ram[0x63A0 + ram[0x6157]]*256 + ram[0x6380 + ram[0x6157]]) >= 0xB12B and (ram[0x63A0 + ram[0x6157]]*256 + ram[0x6380 + ram[0x6157]]) < 0xB16A
  - its script runs 2A.B1C8: ram[0x6133] == 0x4F and (ram[0x63A0 + ram[0x6157]]*256 + ram[0x6380 + ram[0x6157]]) >= 0xB1C8 and (ram[0x63A0 + ram[0x6157]]*256 + ram[0x6380 + ram[0x6157]]) < 0xB1F9
  - its script runs 2A.B198: ram[0x6133] == 0x4F and (ram[0x63A0 + ram[0x6157]]*256 + ram[0x6380 + ram[0x6157]]) >= 0xB198 and (ram[0x63A0 + ram[0x6157]]*256 + ram[0x6380 + ram[0x6157]]) < 0xB1C8
forbid:
  - lost a life: lives < 4
  - lost UFO: ability != 23
  - the mid-boss was hurt: ram[0x6133] == 0x4F and ram[0x61D5] < 25 and ram[0x61D5] > 0
---
Coverage movie (unit en2a). The shelled mid-boss of type $4F in room 185 (2-1 in main's route), met by UFO Kirby.
Kirby never hurts it and floats high above it or far from it when it decides, so that the rows 0-2 of e4f_choices
are drawn (in the corpus Kirby was always near and low: only row 3), and its scripts at 2A:B0E4, 2A:B12B, 2A:B198 and
2A:B1C8, which no movie ran, run.

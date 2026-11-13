---
name: cov3-b-wheelie
start: w12-opus:gw
reference: forbidden
steps:
  - Grand Wheelie (type $49) is in slot 12 of room 176 with 25 hit points: room == 176 and ram[0x6134] == 0x49 and ram[0x61D6] == 25
  - its small wheel (type $49 with variable 0 = 1, slot 14) is out: ram[0x6136] == 0x49 and ram[0x61D8] == 1
  - the small wheel lands and rolls (its variable 5 not 0): ram[0x6136] == 0x49 and ram[0x61D8] == 1 and ram[0x6232] != 0
forbid:
  - lost a life: lives < 4
  - Grand Wheelie was hurt: ram[0x6134] == 0x49 and ram[0x61D6] < 25
---
Coverage movie (unit en2a). Grand Wheelie in room 176 (2-2). Kirby keeps away without hurting it until its third
decision throws the small wheel; the small wheel lands on the floor and rolls (in the corpus it never landed, so
e49_tick_wheel's landing and the rolling paths 2A:AE6F-2A:AEAC never ran).

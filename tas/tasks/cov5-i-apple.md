---
name: cov5-i-apple
start: main@4600
reference: forbidden
steps:
  - in room 50 of 1-2 Kirby goes right far enough for the apple rider (type $13, slot 10) to appear on the right ledge: room == 50 and ram[0x6128+10] == 0x13
  - it rolls left after Kirby, drops to the bottom floor, rolls on left into the wall there and turns (X velocity now positive, left of X 760): room == 50 and ram[0x6128+10] == 0x13 and ram[0x60F2+10] < 0x80 and ram[0x60F2+10] + ram[0x60E0+10] > 0 and ram[0x6086+10]*256 + ram[0x6074+10] < 760
forbid:
  - lost a life: lives < 4
  - dying: hp > 47
---
Coverage movie (cov5, unit en24b). In main the apple rider of room 50 never met a wall. Here Kirby (puffed up) waits
in the upper corridor to the left of the ledge and lets it come: it rolls off the ledge, lands on the bottom floor and
rolls left into the wall at X 720: e13_tick_roll's wall path (24:AB67-AB7B: obj_dir turned by half a circle, e13_roll
again) turns it round. Kirby takes one hit on the way (39 -> 31).

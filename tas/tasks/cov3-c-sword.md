---
name: cov3-c-sword
start: main@64640
reference: forbidden
steps:
  - Sword through the flooded tunnel of 5-2: room == 23 and ability == 3 and x > 690
  - Sword Kirby at the ladder top: room == 23 and ability == 3 and abs(x - 776) < 6 and y < 145 and y > 100
  - back up the ladder with the Sword: room == 23 and ability == 3 and ram[0x5E0] == 3 and y < 80 and frame > 65500
forbid:
  - lost a life: lives < 5
---
Coverage movie for Sword Kirby on a ladder (script $6F of bank 15, never run before). From main just after
the Sword is copied in 5-2 (room 23, frame 64640), swim through the flooded tunnel to the ladder, climb down,
up, down again, slash on the ladder, and climb out at the top.

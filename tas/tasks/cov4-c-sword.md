---
name: cov4-c-sword
start: main@64660
reference: forbidden
steps:
  - Sword Kirby floating on the water of 5-2's flooded tunnel: room == 23 and ability == 3 and ram[0x6291]*256 + ram[0x627F] == 0xA9C4
  - Sword Kirby on the ladder by the thin platforms: room == 23 and ability == 3 and ram[0x6291]*256 + ram[0x627F] == 0xA66C and frame > 67000
  - the Sword dropped with Select and swallowed again: room == 23 and ability == 3 and frame > 68200
  - through the end door of the tunnel with the Sword: room == 28 and ability == 3
  - through the left door of room 28: room == 24 and ability == 3
  - back into an upper chamber of the tunnel room: room == 23 and ability == 3 and frame > 70600
forbid:
  - lost a life: lives < 5
---
Coverage movie for the exits of Sword Kirby's states (bank 15, units kst15, kst_rest, kst_abl, kst_cov3) that no
movie had taken. From main just after the Sword is copied in 5-2 (room 23): a rise ending on the thin platform,
the down thrust into the water, the float and the flap ending in the water, then at the ladder: the ladder from a
walk, a run and a fall, the climb off its lower end, a run into the wall, a turn into the wall, Up during a walk
and after the thrust's landing, Select during the stand, the run and the fall (the star swallowed again each
time), a jump that hits the ceiling, and three doors: from a flap (to room 28), from a jump (to room 24) and from
a fall (back to room 23).

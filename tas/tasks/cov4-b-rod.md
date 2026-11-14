---
name: cov4-b-rod
start: cov3-c-ball@30600
reference: forbidden
steps:
  - after Paint Roller, Kirby drops Ball with Select and its ability star (type 5) bounces in the room: room == 9 and ability == 255 and (ram[0x6128+13] == 5)
  - he takes the Star Rod piece (slot 9 of type 6 is freed) while the star is still there: room == 9 and ram[0x6128+9] != 6 and ram[0x6128+13] != 0xFF
forbid:
  - lost a life: lives < 4
---
Coverage movie (cov4, unit en23). In cov3-c-ball Kirby takes the Star Rod piece Paint Roller leaves with Ball still
copied. Here he presses Select first, so the ability star (type 5) is in the room when he touches the piece:
e06_rod_tick's e06_puff_type (with A = 5) finds it and gives it bank 22's puff (23:A1EE-A208); in the corpus no
object of type 5 was there at that moment.

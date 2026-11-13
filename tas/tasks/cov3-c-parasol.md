---
name: cov3-c-parasol
start: cov2-water-parasol:in
reference: forbidden
steps:
  - Parasol Kirby at the ladder of 2-3's cave: room == 179 and ability == 9 and abs(x - 168) < 5 and y > 100 and y < 160
  - up the ladder with the Parasol: room == 179 and ability == 9 and abs(x - 168) < 6 and y < 100
  - back down the ladder: room == 179 and ability == 9 and abs(x - 168) < 6 and y > 116 and frame > 19300
forbid:
  - lost a life: lives < 3
---
Coverage movie for Parasol Kirby on a ladder (script $C4 of bank 15, never run before). From the
cov2-water-parasol checkpoint in 2-3's flooded cave (room 179), walk to the ladder, climb up and down, swing the
parasol on it, and step off at the top.

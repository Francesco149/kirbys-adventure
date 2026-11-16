---
name: cov11-d-paint
start: w12-sonnet@65400
reference: forbidden
steps:
  - Paint Roller (slot 14, type $44) draws a move across (mark 1) twice in a row, so e44_pick_route doubles $0788 to 2 (2C:A23A): room == 9 and ram[0x6128+14] == 0x44 and ram[0x0788] == 2
  - at the next corner $0788 is 2, so the route is chosen by a random bit (2C:A201) and $0788 starts over at 0: room == 9 and ram[0x6128+14] == 0x44 and ram[0x0788] == 0 and frame > 66500
forbid:
  - lost a life (the start has 0 lives left): lives < 0 or hp == 255
  - hurt twice: hp < 23
---
Coverage movie (batch 11, part D; unit en2c). In every corpus fight Paint Roller's random route picks never drew
two moves across in a row. Here Kirby keeps the fight going for about 25 seconds without beating him; the
picks happen to give mark 1 twice in a row ($0788 = 2, 2C:A23A), and the following pick takes the random-bit
choice at 2C:A201. The inputs were found with random macro sequences checked against the branch targets on the
instrumented core (the draw depends on the random state, which the inputs move only indirectly).

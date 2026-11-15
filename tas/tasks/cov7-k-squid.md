---
name: cov7-k-squid
start: main@46100
reference: forbidden
steps:
  - in 4-2's labyrinth (room 244) main's UFO Kirby reaches the hidden door at the lower right (cell 3, 456,248): ram[0x55F] == 0 and room == 244 and abs(x - 456) <= 6 and abs(y - 248) <= 8
  - Kirby is in the side room 245 that no corpus movie entered, with the two lunging squids (type $1D, variant 2) under the platform: ram[0x55F] == 0 and room == 245 and ram[0x6128+9] == 0x1D and ram[0x6128+13] == 0x1D
  - Kirby waits at the left wall, then hovers in the top left corner while the squids lunge at him; both are gone: ram[0x55F] == 0 and room == 245 and x < 30 and y < 100 and ram[0x6128+9] >= 0x80 and ram[0x6128+13] >= 0x80
forbid:
  - lost a life: lives < 4
  - dying: hp > 47
---
Coverage movie (cov7, unit en26b, also en24b). Main takes the upper door of 4-2's labyrinth (room 244); the hidden
door in its lower right cell leads to room 245, a one-screen room no corpus movie entered, where two squids of type
$1D, variant 2 (e1d_lunge), hang under a platform. Kirby stays on the platform at the left and then hovers in the
corner: the squids lunge at him again and again. New: e1d_lunge_time's near path (26:A3AD-A3B1, the "less than 16
apart" test with the unrelated high byte), e1d_tick_lunge's count running out (26:A319, the lunge again), the walker
turning at the left wall (e1d_tick_walk 26:A0CC) and e1d_tick_jump's wall turn (26:A11D-A121); on the way, the
search through room 244 runs e12_tick 24:A97D-A987.

---
name: cov3-c-ball
start: cov2-abilities-paint:ball
reference: forbidden
steps:
  - Ball form in Paint Roller's arena: world == 1 and room == 9 and ability == 17 and ram[0x5E0] == 11
  - Paint Roller beaten, Ball kept: trans == 5 and ability == 17
  - into 2-2 with Ball: room == 173 and ability == 17
  - Ball form in the Warp Star room: room == 175 and ram[0x5E0] == 11
  - Ball form in the desert: room == 176 and ram[0x5E0] == 11
  - Ball form in the last room of 2-2 (ladder, low ceiling): room == 177 and ram[0x5E0] == 11
forbid:
  - lost a life: lives < 4
---
Coverage movie for Ball Kirby (ability $11, kirby_form $0B, bank 19), which the corpus had only for a few
hundred frames at the end of the Paint Roller fight. From the cov2-abilities-paint checkpoint with Ball, beat
Paint Roller, carry Ball through 2-2 (Warp Star room, the sloped desert, the ladder room) and use the ball form
(B, then A) on slopes, under the low ceiling and on the ladder.

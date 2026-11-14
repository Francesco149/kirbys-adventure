---
name: cov5-h-ball
start: cov3-c-ball@37402
reference: forbidden
steps:
  - the ball at rest in 2-2's last room: room == 177 and ability == 17 and ram[0x6291]*256 + ram[0x627F] == 0xB342
  - A at rest, the ball's jump: room == 177 and ability == 17 and ram[0x6291]*256 + ram[0x627F] == 0xB4DD
  - B at rest, out of the ball: room == 177 and ability == 17 and ram[0x6291]*256 + ram[0x627F] == 0xB31A and frame > 37420
  - rolling: room == 177 and ability == 17 and ram[0x6291]*256 + ram[0x627F] == 0xB3C0 and frame > 37600
  - a jump from rest again, then B in its rise: room == 177 and ability == 17 and ram[0x6291]*256 + ram[0x627F] == 0xB7A9
forbid:
  - lost a life: lives < 4
---
Coverage movie for the pad exits of Ball Kirby's states (unit kst_cov3, bank 19) in 2-2's last room (177), from the end
of cov3-c-ball: A new and B new in kirby_st_ball_stand (scripts $D5 and $D9), B new while rolling
(kirby_st_ball_roll) and B new in the jump's rise (kirby_st_ball_jump_rise), each leaving the ball form.

---
name: cov10-b-ball
start: cov5-h-ball@37849
reference: forbidden
steps:
  - Ball form on the row of blocks under the low ceiling of 2-2's last room: room == 177 and ability == 17 and ram[0x5E0] == 11 and y <= 80 and x >= 200 and x <= 220
  - the jump stopped by the ceiling: kirby_st_ball_jump_rise's kirby_ceiling_bump, script $D7, the ball in the air (19:B546) with no Y speed at the top: room == 177 and ram[0x5E0] == 11 and ram[0x6291]*256 + ram[0x627F] == 0xB546 and y <= 55 and frame < 37910
  - bounces with A held grow until the air state hits the ceiling (kirby_st_ball_air's kirby_ceiling_bump): room == 177 and ram[0x5E0] == 11 and ram[0x6291]*256 + ram[0x627F] == 0xB546 and y <= 55 and frame > 37990
  - the ball at rest on the door at (472, 137): room == 177 and ram[0x5E0] == 11 and ram[0x6291]*256 + ram[0x627F] == 0xB342 and abs(x - 472) <= 4
  - Up there takes the door in ball form (kirby_st_ball_stand's pad_up_door): room == 42 and ability == 17
forbid:
  - lost a life: lives < 4
  - lost the Ball: ability != 17
---
Coverage movie (cov10, unit kst_cov3): Ball Kirby's ceiling and door exits in 2-2's last room (177), from the end of
cov5-h-ball. On the row of blocks under the ceiling at x 210 the ball jumps (A held) into the ceiling: the ceiling exit
of kirby_st_ball_jump_rise (19:B4F7 falls through to script $D7). Holding A on the bounces makes each one higher
(ball_land's factor $0166 with A held) until a bounce hits the ceiling: the ceiling exit of kirby_st_ball_air (19:B56A).
Then the ball rolls to the door at (472, 137), stops on it, and Up takes the door from kirby_st_ball_stand (19:B36F),
into the goal game (room 42).

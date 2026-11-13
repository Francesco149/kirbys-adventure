---
name: cov3-c-mk
start: main:6-7-fight
reference: forbidden
steps:
  - Meta Knight walks up beside Kirby (walk step 1): ram[0x6128+10] == 66 and ram[0x620A] == 1
  - step 2, he faces Kirby: ram[0x6128+10] == 66 and ram[0x620A] == 2
  - Kirby presses a direction and Meta Knight goes back to step 1: ram[0x6128+10] == 66 and ram[0x620A] == 1 and frame > 106060
  - back to the approach: ram[0x6128+10] == 66 and ram[0x620A] == 0 and frame > 106080
forbid:
  - lost a life: lives < 6
---
Coverage movie for Meta Knight's walk beside Kirby (type $42: e42_step_follow, e42_step_face), which before ran
only in the credits' demo fight. In the 6-7 fight Kirby waits until Meta Knight reaches the point beside him
(variable 3 = 1, then 2), then taps Left and Right while he follows: the never-run joypad branches at 2B:B1EF and
2B:B27A, and the return to the approach at 2B:B221.

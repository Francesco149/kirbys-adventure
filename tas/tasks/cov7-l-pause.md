---
name: cov7-l-pause
start: cov4-d-pause@3040
reference: forbidden
steps:
  - Select in the CONTINUE / EXIT STAGE box toggles the choice to 1: room == 43 and ram[0x61CA] == 1 and frame < 3050
  - Select again toggles it back to 0: room == 43 and ram[0x61CA] == 0 and frame > 3052 and frame < 3070
  - CONTINUE chosen, back in 1-1 with hp unchanged: room == 43 and hp == 39 and ram[0x61CA] == 0 and frame > 3150
---
Coverage movie (unit scn_cov4). From cov4-d-pause with the pause screen's CONTINUE / EXIT STAGE box up (1-1 entered
again after it was cleared): Select pressed four times toggles the choice (pause_exit_tick's Select path, 38:B090,
never pressed before), then A takes CONTINUE.

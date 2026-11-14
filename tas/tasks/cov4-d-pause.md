---
name: cov4-d-pause
start: main@2700
reference: forbidden
steps:
  - 1-1 entered again after it was cleared: room == 43 and world == 0 and hp == 39
  - paused, EXIT STAGE chosen, and Kirby is back in the World 1 hub with hp unchanged, 150 frames after entering: room == 0 and world == 0 and hp == 39 and frame < 3150
---
Coverage movie (units rooms2, frame). From the main movie's World 1 hub right after 1-1 was cleared, Kirby enters the
1-1 door again and pauses in its first room: pause_exit_test answers 1 (38:B111, the stage was cleared before), so the
pause screen gets the CONTINUE / EXIT STAGE box (the script at 38:AFF4). The hand goes down, up and down again and EXIT
STAGE is chosen: leave_tail takes its never-run jump to stage_begin (3F:E53E) and Kirby is back at the hub.

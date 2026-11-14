---
name: cov4-d-tower
start: w3-sonnet@56200
reference: forbidden
steps:
  - the pause screen is up in the tower room, scroll_mode 7: room == 205 and ram[0x051E] == 7
  - paused and unpaused in the tower room 205 (Butter Building), still there with the ability kept: room == 205 and world == 2 and ability == 14 and ram[0x051E] != 7 and frame >= 56400
---
Coverage movie (unit rooms2). Kirby pauses in the first tower room ($00CD) of the corpus' World 3 run and unpauses:
the pause's closing script redraws the room with screen_redraw, whose tower-room path (13:A79F: cam_x = scroll_x) no
corpus pause had taken.

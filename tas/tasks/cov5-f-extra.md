---
name: cov5-f-extra
start: cov5-f-sw:extra_menu
reference: forbidden
steps:
  - PLAY EXTRA GAME chosen on the 100% file: the Extra Game flag $F4 is 1, Kirby starts with 2 lives and 3 bars: ram[0x00F4] == 1 and lives == 2 and hp == 23
  - World 1 hub of the Extra Game: room == 0 and world == 0 and ram[0x00F4] == 1
  - 1-1 entered: room == 43 and ram[0x055F] == 0 and ram[0x00F4] == 1
  - 1-1 cleared (the goal game): room == 42 and ram[0x055F] == 0
  - Crane Fever entered from the hub in the Extra Game: room_pick_kind gives it level 3 (minigame_level 2): ram[0x07D1] == 2 and ram[0x00F4] == 1
  - all lives lost in 1-1: the game over screen: lives == 255 and ram[0x00F4] == 1
  - CONTINUE chosen in the continue game, Kirby back with 2 lives and 3 bars: lives == 2 and hp == 23 and ram[0x00F4] == 1
---
Coverage movie (cov5, units hud / rooms / scenes / minigame: the Extra Game). From cov5-f-sw's finished-file menu
with PLAY EXTRA GAME, the Extra Game starts ($F4 = 1, the status bar's 3-bar health, 2 lives). Kirby clears 1-1, which
opens Crane Fever; its door (kind $C) takes room_pick_kind's Extra path (13:A25B, minigame_level 3: three stars on the
card). After the crane he loses every life in 1-1, gets the game over's continue game and continues (continue_setup's
Extra path, 3D:BC5B). About 249,300 frames (see cov5-f-sw about the 200,000-frame limit).

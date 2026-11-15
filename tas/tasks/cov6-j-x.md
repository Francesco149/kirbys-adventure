---
name: cov6-j-x
start: cov5-f-extra@237669
reference: forbidden
steps:
  - PLAY EXTRA GAME chosen quickly (the file select's idle RNG call avoided): game_mode 1, 2 lives, 3 bars: ram[0x00F4] == 1 and lives == 2 and hp == 23
  - the Extra Game's World 2 hub: room == 1 and world == 1 and ram[0x00F4] == 1
  - the Extra Game's World 3 hub: room == 2 and world == 2 and ram[0x00F4] == 1
  - the Extra Game's World 4 hub: room == 3 and world == 3 and ram[0x00F4] == 1
  - the Extra Game's World 5 hub: room == 4 and world == 4 and ram[0x00F4] == 1
  - the Extra Game's World 6 hub (Heavy Mole beaten): room == 5 and world == 5 and ram[0x00F4] == 1
  - the Extra Game's World 7 hub (Meta Knight beaten): room == 6 and world == 6 and ram[0x00F4] == 1
  - the Fountain of Dreams in the Extra Game: room == 15 and world == 7 and ram[0x00F4] == 1
  - Nightmare's last form in the Extra Game: room == 16 and world == 7 and ram[0x00F4] == 1
  - the Extra Game cleared: save_game_complete's game_mode path stores byte 3 = 9: ram[0x0528] == 9 and ram[0x00F4] == 1
  - THE END: room == 18 and ram[0x0528] == 9
  - after the reset the file is saved with byte 3 = 9 (100% PERFECT, LISTEN TO SOUNDS): ram[0x7906] == 9 and ram[0x7905] == 63 and world == 0
  - the sound test's last song and last sound effect chosen: ram[0x07E8] == 0x39 and ram[0x07E9] == 0x57
---
Coverage movie (cov6, the Extra Game finished and the sound test; units scenes3 / cov5_tour / sound / snddata / hud /
bosses). From cov5-f-extra's file select (the 100% file of cov5-f-sw), PLAY EXTRA GAME is chosen within 40 frames and
the opening is skipped at the same moment as in `main`, so the Extra Game starts with main's RNG and frame counter.
The movie replays main's input game frame by game frame (lag-aware), with small input fixes where the slowdown
differs, and search-played repairs wherever the Extra Game's three bars or a different enemy made it part ways with
main (mid-bosses, Meta Knight's duel with one death and a return from the hub, World 7's arenas, King Dedede, the
Power Orb and Nightmare by staged searches), hub and door resyncs (position and frame counter) keeping main's UFO-form
glitch through worlds 4-7. The ending stores byte 3 = 9 (save_game_complete 3D:BD12), the credits and THE END play,
Start resets to the title; the file select shows "100% : PERFECT" and "~ Super Star ~" and file 1's menu LISTEN TO
SOUNDS (fsel state 8): every song (0-$39, the 25 never-started ones for 1,500 frames each) and every sound effect
(0-$57) is played, then QUIT. About 458,750 frames.

---
name: cov5-f-sw
start: cov2-save-finished:menu
reference: forbidden
steps:
  - the finished file (byte 2 = 46, no switch pressed) continued into the World 7 hub: room == 6 and world == 6 and ram[0x7905] == 46 and ram[0x052B] + ram[0x052C] + ram[0x052D] + ram[0x052E] + ram[0x052F] == 0
  - 7-1's switch (UFO from a mix in room 110, its big star through the metal wall): ram[0x052F] & 0x01
  - 7-6's switch (the moon door of the last room): ram[0x052F] & 0x20
  - 6-4's switch: ram[0x052E] & 0x08
  - 6-6's switch (Fireball from a mix in the first room): ram[0x052E] & 0x20
  - 6-5's switch (the fuse lit with a Fireball dash, the cannon to room 96): ram[0x052E] & 0x10
  - 6-2's switch (Stone from the World 5 museum pounds the stake): ram[0x052E] & 0x02
  - 6-1's switch (Stone): ram[0x052E] & 0x01
  - 6-3's switch (Hammer from the mid-boss, Fire from a Hot Head swallowed by the underwater fuse, the cannon): ram[0x052E] & 0x04
  - 5-5's switch (Hi-Jump breaks the star blocks, Fire lights the fuse, the cannon): ram[0x052D] & 0x10
  - 5-1's switch: ram[0x052D] & 0x01
  - 5-4's switch (the hidden door of room 293): ram[0x052D] & 0x08
  - 4-6's switch: ram[0x052C] & 0x20
  - 4-3's switch: ram[0x052C] & 0x04
  - 4-1's switch (the hidden door in the star-block grid): ram[0x052C] & 0x01
  - 3-1's switch (Hi-Jump from the World 3 museum): ram[0x052B] & 0x01
  - 3-6's switch: ram[0x052B] & 0x20
  - 5-6's switch (Hammer from a mix breaks the island's metal blocks under water): ram[0x052D] & 0x20 and ram[0x7905] == 63
  - after a soft reset, file 1 at 100% on the file select and its menu open (CONTINUE / PLAY BONUS GAMES / PLAY EXTRA GAME / QUIT): world == 0 and ram[0x7905] == 63 and ram[0x7906] == 8
---
Coverage movie (cov5, units scenes / scenes3 / tail2: the 100% file). From the corpus' finished file (cov2-save-finished,
71%: every stage and the game cleared, no Big Switch), Kirby presses all 17 Big Switches, world by world from World 7 back
to World 3 (the hubs' kind 30 doors lead to the previous world's hub), leaving each stage by the pause screen's EXIT
STAGE after the switch's hub pan. The file's byte 2 reaches 63 (save_count; save_game's 100% tests 3D:BD61 / 3D:BD7C).
After a soft reset the file select shows "KIRBY 1...100% : EXTRA" and "~Hero of Lore~", and file 1's menu has PLAY
EXTRA GAME (fsel_rows / fsel_percent's 100% paths, fsel_finished_text's third row). The movie is about 237,900
frames: env.parse_spec's 200,000-frame limit has to be raised before kt check / kd gain / kd corpus add can read it.

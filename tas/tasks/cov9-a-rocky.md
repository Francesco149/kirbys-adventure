---
name: cov9-a-rocky
start: main@64100
reference: forbidden
steps:
  - in World 4's hub (LEVEL 5) at the door of 5-1, already cleared: room == 4 and world == 4 and frame < 64110
  - paused with SPARK (ability 1): the pause screen shows its text: room == 18 and ability == 1 and ram[0x051E] == 7
  - paused with CUTTER (ability 2): the pause screen shows its text: room == 18 and ability == 2 and ram[0x051E] == 7
  - paused with SWORD (ability 3): the pause screen shows its text: room == 18 and ability == 3 and ram[0x051E] == 7
  - paused with LASER (ability 5): the pause screen shows its text: room == 18 and ability == 5 and ram[0x051E] == 7
  - paused with MIKE (ability 6): the pause screen shows its text: room == 18 and ability == 6 and ram[0x051E] == 7
  - paused with SLEEP (ability 10): the pause screen shows its text: room == 18 and ability == 10 and ram[0x051E] == 7
  - paused with NEEDLE (ability 11): the pause screen shows its text: room == 18 and ability == 11 and ram[0x051E] == 7
  - paused with ICE (ability 12): the pause screen shows its text: room == 18 and ability == 12 and ram[0x051E] == 7
  - paused with FREEZE (ability 13): the pause screen shows its text: room == 18 and ability == 13 and ram[0x051E] == 7
  - paused with BALL (ability 17): the pause screen shows its text: room == 18 and ability == 17 and ram[0x051E] == 7
  - paused with TORNADO (ability 18): the pause screen shows its text: room == 18 and ability == 18 and ram[0x051E] == 7
  - paused with CRASH (ability 19): the pause screen shows its text: room == 18 and ability == 19 and ram[0x051E] == 7
  - paused with LIGHT (ability 20): the pause screen shows its text: room == 18 and ability == 20 and ram[0x051E] == 7
  - paused with BACK DROP (ability 21): the pause screen shows its text: room == 18 and ability == 21 and ram[0x051E] == 7
  - paused with THROW (ability 22): the pause screen shows its text: room == 18 and ability == 22 and ram[0x051E] == 7
---
Coverage movie (batch 9, part A): the pause texts of fifteen abilities (pause_desc_lo / _hi entries 2-23,
pause_text_spark ... pause_text_throw) in one movie. From main in World 4's hub, into 5-1 (room 17) and through its
first door to the detour room 18, where two Rockys stand side by side. Inhaling both and swallowing starts the mix
(mix_step, 4 frames a step on the first lap, from Stone + 1); A stops it on the ability wanted, and Start then
opens the pause screen with that ability's text (Start is ignored while kirby_flags bit 7 is set, ~75 frames
after the swallow, and during the mix itself). To get the Rockys back, Kirby falls off the platform after each
pause and respawns in room 18 (a life each). main's Kirby flies with the UFO-style movement while kirby_ability is
$FF (main's carried state), so he cannot inhale: the first fall resets him. At lives 0 the game over is taken twice:
CONTINUE replays World 4's level card and the hub, and Kirby walks 5-1's room 17 again. After Spark the pause's
EXIT STAGE was used instead (one more walk through room 17).

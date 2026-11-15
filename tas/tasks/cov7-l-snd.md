---
name: cov7-l-snd
start: cov6-songs@433669
reference: forbidden
steps:
  - Right on the MUSIC row at $39 wraps the number to 0: ram[0x07E8] == 0 and frame < 433700
  - Left at 0 wraps it back to $39: ram[0x07E8] == 0x39 and frame > 433690 and frame < 433720
  - Left on the SOUND EFFECT row at 0 wraps to $57: ram[0x07E9] == 0x57
  - Right at $57 wraps to 0: ram[0x07E9] == 0 and frame > 433750 and frame < 433780
  - sound 0 started with A: ram[0x07EB] == 1
  - B while it plays stops it: ram[0x07EB] == 0 and frame > 433790 and frame < 433820
  - B on the idle SOUND row left the sound test (variable 9 of slot 0 no longer 8): ram[0x626C] != 8 and frame > 433800 and frame < 433900
  - LISTEN TO SOUNDS entered a third time: ram[0x626C] == 8 and frame > 434150
  - B on the idle MUSIC row leaves it again: ram[0x626C] != 8 and frame > 434200
---
Coverage movie (unit cov6_extra, scenes). From the end of cov6-songs (the sound test, MUSIC row at $39): Right wraps
the song number to 0 (3D:B3ED) and Left back to $39 (3D:B3F1, also fsel_input_snd's Left at 3D:B34C); on the SOUND
EFFECT row Left at 0 gives $57 (3D:B434) and Right at $57 gives 0 (3D:B430); A plays sound 0 and B while it plays
stops it (snd_test_stop 3D:B0E5). B on the idle SOUND row leaves the sound test (3D:B0F0, A = 1); LISTEN TO SOUNDS
is entered again and B pressed on the QUIT row (3D:B0CF taken), then a third time and B on the idle MUSIC row
(3D:B0D4 taken). Scripted input, no search.

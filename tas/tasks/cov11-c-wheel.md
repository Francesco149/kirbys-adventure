---
name: cov11-c-wheel
start: main@30860
reference: forbidden
steps:
  - in room 207 UFO Kirby shoots the bomb block that opens the lower-left passage and takes its door (cell 2, col 6, row 8) into room 209, which no movie had loaded: room == 209
  - the Grand Wheelie of class 0 there (kind $B4, type $49, slot 9) fights in this walled one-screen room with sloped corners: room == 209 and ram[0x6128+9] == 0x49 and ram[0x61CA+9] == 25
  - Kirby keeps out of its way for about 2,400 frames, unhurt, while it rolls, brakes and throws its small wheels: room == 209 and ram[0x6128+9] == 0x49 and hp == 47 and frame >= 33400
  - then it is beaten without a hit on Kirby: room == 209 and ram[0x6128+9] == 0x49 and ram[0x61CA+9] == 0 and hp == 47
forbid:
  - lost a life: lives < 4
  - hurt: hp < 47
---
Coverage movie (batch 11, part C; unit en2a). Room 209 (from room 207's lower-left door, behind a bomb block) holds a
Grand Wheelie of class 0 ($B4) that no movie had met: the class-0 wheel was seen only in the seven-screen room 176.
Here it fights in a one-screen room with walls and sloped corners, the setting of the triage's wall leads (a brake into
a wall, a small wheel rolling or flying into a wall, a feint into a wall). UFO Kirby dodges for ~2,400 frames without
being hit, then shoots it down.

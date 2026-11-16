---
name: cov11-c-lion
start: main@76420
reference: forbidden
steps:
  - in room 303 (world 5) UFO Kirby takes the door at cell 0, col 14, row 9 instead of main's door to 302, into room 301, which no movie had loaded (the room variable holds the low byte, 45): room == 45 and world == 4
  - the mane mid-boss of class 0 there (kind $BE, type $4D, slot 11) wakes in the pit in the middle of the room: room == 45 and ram[0x6128+11] == 0x4D and ram[0x61CA+11] == 27
  - Kirby keeps out of its way for about 1,200 frames, unhurt: room == 45 and ram[0x6128+11] == 0x4D and hp == 31 and frame >= 78000
  - then it is beaten without a hit on Kirby: room == 45 and ram[0x6128+11] == 0x4D and ram[0x61CA+11] == 0 and hp == 31
forbid:
  - lost a life: lives < 6
  - hurt: hp < 31
---
Coverage movie (batch 11, part C; unit en2a). Room 301 holds the only stage-room mane mid-boss of class 0 ($BE); the
corpus had never loaded the room (main leaves room 303 by the door to 302). UFO Kirby enters it, flies to the pit in
its middle where the mane wakes, dodges it for ~1,200 frames and shoots it down. Its class-0 plan (2A:A2FF's
fall-through, e4d_plan_states) runs in a stage room rather than the arena.

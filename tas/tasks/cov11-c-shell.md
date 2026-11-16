---
name: cov11-c-shell
start: main@82900
reference: forbidden
steps:
  - in room 61 UFO Kirby swims to the door under the water at cell 4, col 7, row 0 (main took the door to 63) and enters room 62, which no movie had loaded: room == 62
  - the shell mid-boss of class 0 there (kind $B8, type $4B, slot 10) fights in the one-screen room with water at its bottom: room == 62 and ram[0x6128+10] == 0x4B and ram[0x61CA+10] == 30
  - Kirby keeps out of its way for about 600 frames: room == 62 and ram[0x6128+10] == 0x4B and hp == 39 and frame >= 83700
  - then it is beaten: room == 62 and ram[0x6128+10] == 0x4B and ram[0x61CA+10] == 0
forbid:
  - lost a life: lives < 6
  - hurt twice: hp < 31
---
Coverage movie (batch 11, part C; unit boss_cov3 / en29). Room 62 (from the underwater door of room 61) holds the shell
mid-boss of class 0 ($B8) in a closed one-screen room whose floor is water; the corpus had never loaded it. UFO Kirby
enters, dodges it for ~600 frames, takes one hit and shoots it down.

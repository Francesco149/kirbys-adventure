---
name: cov11-c-arena7
start: main@111360
reference: forbidden
steps:
  - in room 113 (world 7) UFO Kirby takes the lower door instead of the upper one, into room 114, the first fight of the chain 114-126: room == 114
  - the first mid-boss (script $22, slot 13) is beaten after its fight: room == 114 and ram[0x6128+13] == 0x22 and ram[0x61CA+13] == 0 and frame > 111700
  - room 116 (never loaded before): the turtle of class 0 (kind $BA, type $4F, slot 13) fights: room == 116 and ram[0x6128+13] == 0x4F
  - room 122 (never loaded before): the shell mid-boss of class 0 (kind $B8, type $4B, slot 11) fights: room == 122 and ram[0x6128+11] == 0x4B
  - room 124 (never loaded before): the beetle of class 0 (kind $B6, type $4A, slot 11) fights: room == 124 and ram[0x6128+11] == 0x4A
  - room 126 (never loaded before): the mane mid-boss of class 0 (kind $BE, type $4D, slot 11) fights: room == 126 and ram[0x6128+11] == 0x4D and ram[0x61CA+11] > 0
  - it is beaten without Kirby taking a hit in this room: room == 126 and ram[0x6128+11] == 0x4D and ram[0x61CA+11] == 0 and hp == 7
forbid:
  - lost a life: lives < 6
---
Coverage movie (batch 11, part C; units en29, en2a, boss_cov3/4). Room 113's lower door leads to a chain of arena
rooms, 114 to 126 (fights in the even rooms, passages in the odd ones), that no movie had entered: the class-0
variants of the turtle ($BA, room 116), the shell ($B8, room 122), the beetle ($B6, room 124) and the mane ($BE, room
126) had never been loaded. UFO Kirby (the UFO kept from world 7's start, ability reads $FF) shoots his way through
all seven fights; the mane of class 0 runs its class-0 plan step (2A:A2FF) and is beaten.

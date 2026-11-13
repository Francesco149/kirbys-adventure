---
name: cov3-b-scarfy
start: main@65640
reference: forbidden
steps:
  - Scarfy (type $40) in slot 13 of room 28 is angry and chases Kirby (state 3): room == 28 and ram[0x6135] == 0x40 and ram[0x620D] == 3
  - its chase runs out (state 4, the end): ram[0x6135] == 0x40 and ram[0x620D] == 4
forbid:
  - lost a life: lives < 5
---
Coverage movie (unit en26b). In room 28 Kirby half-inhales a calm Scarfy, which turns angry and chases him; Kirby
keeps out of its reach for the whole $78 frames of the chase, so the end of the chase (26:BCFD, state 4 at 26:BD0B
and the burst script 26:BBA2) runs: in the corpus every chase ended earlier.

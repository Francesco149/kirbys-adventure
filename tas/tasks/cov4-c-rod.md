---
name: cov4-c-rod
start: main:8-wizard-fight
reference: forbidden
steps:
  - Star Rod run into a swing (B during the run): room == 16 and ability == 24 and ram[0x6291]*256 + ram[0x627F] == 0xA7FB and frame < 135030
  - Star Rod run into a crouch (Down during the run): room == 16 and ability == 24 and ram[0x6291]*256 + ram[0x627F] == 0xA624 and frame > 135330
  - still holding the rod at the end: room == 16 and ability == 24 and frame > 135770
forbid:
  - lost a life: lives < 8
---
Coverage movie for the pad exits of the Star Rod's run, skid and rise (bank 17, unit kst17) in Nightmare's
wizard fight (room 16): A, B, Down and Up during a run, B during the skid, Up during the rise, a run into the
screen's left edge. The arena has no ladder, door, water or ledge, and Select never drops the rod (bit 5 of
kirby_flags is set all through the Star Rod fights), so the other exits of these states cannot be taken here.

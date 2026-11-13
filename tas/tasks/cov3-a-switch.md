---
name: cov3-a-switch
start: w3-sonnet@53600
reference: forbidden
steps:
  - Hi-Jump Kirby in 3-1's blue-walled room: room == 202 and world == 2 and ability == 14
  - by the bottom door into room 203: room == 203
  - back in room 202 by 203's upper door, inside the closed box of the switch: room == 202 and y < 180 and x > 85 and x < 195 and ram[0x6128+9] == 111
  - the switch is pressed (3-1's flag in the row after stages_done, $052B, is set): room == 202 and ram[0x052B] != 0
  - sent back to the World 3 hub: room == 2 and world == 2 and ram[0x052B] != 0
forbid:
  - lost a life: lives < 4
  - hit: hp < 47
---
Coverage movie (cov3, unit en29): the Big Switch of 3-1 (type $6F on its pedestal), which no corpus movie pressed.
From w3-sonnet entering room $CA with Hi-Jump, Kirby takes the bottom door to room $CB, takes its upper door
into the switch's closed box, presses the switch and is returned to the hub, where the Arena door opens.

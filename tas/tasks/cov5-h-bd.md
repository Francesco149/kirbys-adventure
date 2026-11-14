---
name: cov5-h-bd
start: w3-sonnet@60850
reference: forbidden
steps:
  - Bugzzy inhaled whole: room == 210 and mouth == 21
  - Back Drop copied: room == 210 and ability == 21
  - an enemy grabbed in room 204 (kirby_action $0C): room == 204 and ability == 21 and ram[0x5E1] == 12
  - the grab timed out or was thrown, the held object told 3 ($05FC): room == 204 and ability == 21 and ram[0x5FC] == 3
  - a throw backwards, the held object told 1: room == 204 and ability == 21 and ram[0x5FC] == 1
  - a throw forwards into the next room: room == 205 and ability == 21 and ram[0x5FC] == 1
forbid:
  - lost a life: lives < 4
---
Coverage movie for Back Drop's moves (units kst18, kst_abl, kst_rest): w3-sonnet's Bugzzy (room 210, normal-form
Kirby) is inhaled whole and swallowed, which copies Back Drop (ability $15; the corpus had only Throw, $16, outside
the attract demo). Out through the goal game and the hub through the hub's door 2 into room 204, Kirby grabs enemies and lets
grab_choose pick each move: no input until variable 2 runs out (the random move of 16:A6DC), a grab in the air (move
6, scr_16_A966, $05FC = 3), Up, Down, A, the direction behind him (move 4, scr_16_A7BD) and the direction he faces
(move 2, scr_16_A753, into room 205); kfx_held_tick sees $05FC = 1 and 3.

---
name: cov10-b-rodfly
start: cov3-c-rod@134930
reference: forbidden
steps:
  - the flight with the Star Rod at the bottom of room 15, the camera close to its lowest point: room == 15 and ability == 24 and ram[0xE1]*256 + ram[0xE0] >= 0x035B and ram[0x6291]*256 + ram[0x627F] == 0xBB3C
  - B fires: the flight during the shot (kirby_st_rodfly_shot, 17:BC24): room == 15 and ram[0x6291]*256 + ram[0x627F] == 0xBC24 and ram[0xE1]*256 + ram[0xE0] == 0x035C
  - the camera reaches $035D while the shot is on: rodfly_cam_low answers carry in kirby_st_rodfly_shot, script $EC (kirby_s_rodfly_fall): room == 15 and ram[0xE1]*256 + ram[0xE0] == 0x035D and ram[0x6291]*256 + ram[0x627F] != 0xBC24 and ram[0x6291]*256 + ram[0x627F] != 0xBB3C
  - he falls out of the room and loses the life: hp == 255
forbid:
  - left the flight early: room != 15
---
Coverage movie (cov10, unit kst17): the camera exit of kirby_st_rodfly_shot (17:BC36). In the Star Rod's flight
against Nightmare's orb (room 15) the camera scrolls down on its own; when its Y reaches $035D rodfly_cam_low answers
carry and Kirby falls out (script $EC, kirby_s_rodfly_fall, then kirby_s_die). cov3-c-rod reached it from
kirby_st_rodfly; this branch of it, from cov3-c-rod@134930, fires with B at 134961 so that the 7 frames of the shot
(kirby_st_rodfly_shot) are running when the camera gets to $035D at 134968, and the exit is taken there instead.

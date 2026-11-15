---
name: cov9-b-kracko
start: main@59542
reference: forbidden
steps:
  - Kracko's climb in 3-7 (room 11), the UFO dropped with Select (kirby_form 0): room == 11 and ram[0x05E0] == 0 and ram[0x6128+15] == 61
  - Kirby floats (kirby_action $0D) for $78 frames in a row: e3d_eye_hit makes the eye's variable 6 negative: room == 11 and ram[0x6128+15] == 61 and ram[0x6245] >= 0x80
  - e3d_kirby_test starts the chase, state 3 (e3d_st_chase): room == 11 and ram[0x6128+15] == 61 and ram[0x620F] == 3
  - Kirby exhales and stops floating; the eye calms down (state 0 at once, not a charge): room == 11 and ram[0x05E1] != 13 and ram[0x620F] == 0
  - the fight at the top (eye on e3d_tick_fight 2F:AE4C): room == 11 and ram[0x629F]*256 + ram[0x628D] == 0xAE4C
  - Kirby survives the attacks until e3d_pick takes entry 1 (e3d_pick1) and picks attack 4 ($0784 = $80, state 4): room == 11 and ram[0x0784] == 0x80 and ram[0x620F] == 4
  - a walker drops from the cloud (e3d_walker: type $3D, variable 0 = 8; $0789 = 1): room == 11 and ram[0x0789] == 1
forbid:
  - lost a life: lives < 4
---
Coverage movie (cov9, unit dead_en2 / en2f). In main Kirby climbs Kracko's room as the UFO (kirby_form $0D), which
cannot float, so kirby_action was never $0D in the climb. From main@59542 Kirby drops the UFO with Select, floats for
more than 120 frames while the eye watches (e3d_eye_hit counts variable 6 up at 2F:A141 and sets it to $80), the
next e3d_hover / e3d_brake / e3d_steer call of e3d_kirby_test starts the chase (state 3, e3d_st_chase: the eye
steers at the floating Kirby); Kirby exhales and the random number gives the calm path (velocity 0, state 0). At the
top Kirby survives without hurting the boss until e3d_pick runs entry 1 (e3d_pick1, $0785 = 1), which picks attack
4: a walker (e3d_walker) falls from the cloud and walks at Kirby.

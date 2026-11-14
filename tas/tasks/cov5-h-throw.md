---
name: cov5-h-throw
start: cov2-abilities-throw@53420
reference: forbidden
steps:
  - Throw carried out of the museum room into room 3: room == 3 and ability == 22
  - a Waddle Dee caught (kirby_action $0C): room == 3 and ability == 22 and ram[0x5E1] == 12
  - thrown forward with B, Up not held (kirby_s_throw's forward branch, $05FC = 4): room == 3 and ability == 22 and ram[0x5FC] == 4 and frame < 53900
  - another catch and a throw facing left with Down held: room == 3 and ability == 22 and ram[0x5FC] == 4 and frame > 54000
  - one more facing right, Down held until the object flies: room == 3 and ability == 22 and ram[0x5FC] == 4 and frame > 54200
forbid:
  - lost a life: lives < 4
---
Coverage movie for the Throw ability ($16, unit kst_abl): in the World 4 hub's room 3 Kirby catches Waddle Dees and
throws them with B without Up (throw_up_test's other path, kirby_s_throw's forward branch 16:A6EA, which the corpus
never took: its only throws were upward), once facing left (kfx_thrown_vel's left index) and with Down held
(kfx_thrown_vel's Down row).

---
name: cov5-h-light
start: cov2-abilities-light@40710
reference: forbidden
steps:
  - Light carried out of the dark room 234 into the lit room 235: room == 235 and ability == 20 and ram[0x67F1] == 0x32
  - Light used left of the screen's middle, in the lit room: room == 235 and ability == 255 and x < 100
forbid:
  - lost a life: lives < 4
---
Coverage movie for the Light ability's effect (unit kst_abl): cov2-abilities-light copies Light in the dark room 234;
here Kirby carries it through the door into room 235, which is not dark (room_pal $32), and uses it at X 86, left
of the middle of the screen: kfx_light_room takes the not-dark path (variable 0 = 0, 16:AE73-AE77) and the light,
aimed up and to the right at (128, 40), runs kfx_light_tick's paths for a direction other than straight up.

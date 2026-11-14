---
name: cov5-h-lock
start: main@81200
reference: forbidden
steps:
  - UFO Kirby at the right edge of the scrolling Heavy Mole arena: room == 12 and ram[0x95]*256 + ram[0x83] >= ram[0xDE]*256 + ram[0xDD] + 239
  - flying up against the top edge: room == 12 and ram[0xCB]*256 + ram[0xB9] <= ram[0xE1]*256 + ram[0xE0] + 28 and vy < 0
  - the fight kept going until the scroll passes $300 and the room wraps two screens back: room == 12 and frame > 84000 and ram[0xDE]*256 + ram[0xDD] < 0x200
forbid:
  - lost a life: lives < 6
---
Coverage movie for kirby_move_locked (unit kmove): in the Heavy Mole fight (world 4, room 12, cam_locked set, the
camera scrolls by itself) main's UFO Kirby flies to the right edge of the screen, where the right limit (camera +
239) holds him (21:9797 and kirby_edge_test's offsets -7), then up to the top edge, where the top limit (camera Y +
28) holds him (21:97C0). Then he stays alive in the fight without shooting for about 3,300 frames, until the
camera's scroll reaches $300 and scroll_update's room-12 path takes the camera, the scroll, the drawn columns and the
objects back by $200 (3F:E733).

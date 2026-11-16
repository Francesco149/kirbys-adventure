---
name: cov11-a-sink
start: main@82970
reference: forbidden
steps:
  - in room 61 the creature of type $1B created in the water (slot 13) sinks (e1b_tick_sink 25:B2F5) while Kirby keeps away from it: room == 61 and ram[0x6128+13] == 0x1B and ram[0x6290+13]*256 + ram[0x627E+13] == 0xB2F5
  - it reaches the floor of the pool and walks there (e1b_tick_wet 25:B2D9, entered by 25:B303-B30C): room == 61 and ram[0x6128+13] == 0x1B and ram[0x6290+13]*256 + ram[0x627E+13] == 0xB2D9
  - Kirby's water spit hits it on the floor and it is gone: room == 61 and ram[0x6128+13] != 0x1B and frame > 83190
forbid:
  - lost a life: lives < 6
  - hurt: hp < 47
---
Coverage movie (batch 11, part A; unit en25b). In main the type $1B created in room 61's pool was hit while it was
still sinking. Here Kirby waits at the left: it sinks to the pool floor (e1b_tick_sink takes 25:B303 to entry 4 of
e1b_scripts, e1b_wet), walks on the floor with e1b_tick_wet, and Kirby's water spit hits it there (25:B2E0).

---
name: cov10-c-squid
start: main@126140
reference: forbidden
steps:
  - in room 158 (the pier over the water) UFO Kirby hovers left of the gap in the pier while a walking squid (type $1D, variant 0, slot 12) walks on the pier's right part: room == 158 and x < 784 and ram[0x6128+12] == 0x1D and ram[0x629C]*256 + ram[0x628A] == 0xA0BD
  - the squid walks off the end of the pier, falls and e1d_hit finds water at its place (entry 2 of e1d_scripts; tick routine 26:A130): room == 158 and ram[0x6128+12] == 0x1D and ram[0x629C]*256 + ram[0x628A] == 0xA130
  - it swims (tick routine 26:A16D): room == 158 and ram[0x6128+12] == 0x1D and ram[0x629C]*256 + ram[0x628A] == 0xA16D
  - it leaps out of the water back onto the pier and walks again (e1d_tick_walk): room == 158 and ram[0x6128+12] == 0x1D and ram[0x629C]*256 + ram[0x628A] == 0xA0BD and ram[0x6086+12]*256 + ram[0x6074+12] >= 784 and frame > 127000
forbid:
  - lost a life: lives < 8
---
Coverage movie (batch 10, part C; unit en26b). Room 158 is a pier over water with walking squids of type $1D on its
right part; main flies over them as the UFO without stopping. Here UFO Kirby stops left of the gap in the pier (out of
reach of the coconuts) and waits: a walker walks toward him, takes e1d_tick_walk's no-floor exit off the end of the
pier (e1d_walk_fall), and e1d_hit finds water at its position (26:A1A9, entry 2 of e1d_scripts): the water scripts
and tick routines 26:A130-26:A1AD run for the first time (it sinks, swims, leaps out and lands on the pier, where it
walks again). The lunging variant's water path (26:A332, entry 8) stays unreached: the only lunging squid of a room
with water sits at the top of room 158 and leaves the room upward.

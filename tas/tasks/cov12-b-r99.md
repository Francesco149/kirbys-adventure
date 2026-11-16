---
name: cov12-b-r99
start: main@101240
reference: forbidden
steps:
  - in room 99 (world 5), once the bomb blocks are gone, UFO Kirby takes the upper door (cell 0, $C5) instead of the lower one, into room 100 (never loaded before): room == 100
  - in room 100 the two mid-bosses of type $22 (kind $BC, slots 10 and 11) are beaten with UFO shots: room == 100 and ram[0x6128+10] != 34 and ram[0x6128+11] != 34 and frame > 101500
  - the door that appears in room 100 leads to room 101 (never loaded before): room == 101
  - room 101's door (cell 0, $D6) leads to room 102 (never loaded before): room == 102
  - Kirby crosses room 102's five screens to its door (cell 4, $C8) into room 105: room == 105
forbid:
  - lost a life: lives < 6
  - took a hit (main has hp 7 here, so a hit is a lost life): hp < 7 or hp > 47
---
Coverage movie (batch 12, part B). In room 99 (world 5) the shot of UFO Kirby (main's glitched UFO, ability reads
$FF) clears the bomb blocks and opens two doors; main took the lower one (to room 103). The upper one (cell 0, $C5)
leads to the chain 100 -> 101 -> 102 -> 105 that no movie had loaded: room 100 is a castle wall with two mid-bosses
of type $22 (kind $BC; bomb-throwing jugglers) that UFO Kirby beats with his shots (the search had charged shots available) without taking a hit (main has 7 HP); the door that
appears then leads to room 101 (two ledges over water, an enemy of type $26), and room 101's door to room 102, five
screens with slopes (enemies of types $17, $29, $11, $0E, $0F, $16, $38 and a pickup), whose last door leads into
room 105.

---
name: secret-ufo
start: 1-1-speed:r44_start
reference: forbidden
steps:
  - secret room entered: world == 0 and stage == 0 and room not in (0, 42, 43, 44, 45)
  - UFO copied in the secret room: ability == 23 and room not in (0, 42, 43, 44, 45)
  - final area reached as UFO: world == 0 and room == 45 and ability == 23
  - 1-1 goal game: world == 0 and room == 42
  - back in the W1 hub: world == 0 and room == 0
forbid:
  - lost a life: lives < 4
---
A "showcase a secret" task. All you know about the secret is what the online guides say: read
`knowledge/secrets.md` ("1-1: the invisible door to the UFO room") first. No existing movie visits it.

The movie starts from a verified library prefix: the 1-1-speed trace from power-on to the first frames of 1-1's
second area (room 44, frame 1,413: no ability, full HP, 4 lives). From there, in this order:
1. find and enter the invisible door (the secret room's id is unknown; any room of 1-1 other than 43, 44, 45);
2. copy UFO from the enemy inside (ability id 23 = $17);
3. leave, and carry UFO through the rest of the stage into the final area (room 45);
4. clear 1-1 (goal game) and return to the hub.

No life may be lost. A hit can knock the ability out, so guard `ability` in your searches once you have it.

The point is to measure how the recipe handles a goal that is only described in prose by a guide: turning the
description into RAM predicates, finding an unmarked door, and keeping a constraint. The trace doubles as a demo
clip, so prefer clean play over frame count. Report the cost per step and what the recipe got wrong or lacked.
Expected budget: ~$3-6.

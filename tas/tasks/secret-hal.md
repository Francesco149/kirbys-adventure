---
name: secret-hal
start: 1-1-speed:final
reference: forbidden
steps:
  - 1-2 entered: world == 0 and room == 47
  - past the Warp Star on foot: room == 47 and x >= 1000
  - among the HAL blocks: room == 47 and x >= 1340 and x <= 1500
  - next area reached afterwards: world == 0 and room == 48
forbid:
  - lost a life: lives < 4
---
A "showcase a secret" task. All you know about the secret is what the online guides say: read
`knowledge/secrets.md` ("1-2: the HAL room") first. No existing movie visits it.

The movie starts from a verified library prefix: the 1-1-speed trace from power-on to the World 1 hub after
clearing 1-1 (frame 3,159: no ability, full HP, 4 lives). From there, in this order:
1. enter 1-2 (its first area is room 47);
2. make the Warp Star disappear with the trick the guides describe, and walk past where it was (the Warp Star
   normally takes Kirby away at x of about 900, so `x >= 1000` in room 47 proves the trick worked);
3. reach the Star Blocks that spell "HAL" (x between 1340 and 1500 in room 47);
4. go back, take the Warp Star (the guides say it is there again) and arrive in the next area (room 48).

No life may be lost. The Shotzo and the Gordo in this room cannot be killed.

The point is to measure how the recipe handles a goal that depends on a mechanic only described in prose
(an object leaving and re-entering the view): you will have to find out what "disappears from view" means in RAM
terms (the object slots, the camera) and search or probe for the exact turning point. The trace doubles as a demo
clip. Report the cost per step and what the recipe got wrong or lacked. Expected budget: ~$3-6.

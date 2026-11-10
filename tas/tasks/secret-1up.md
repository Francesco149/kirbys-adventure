---
name: secret-1up
start: w12-sonnet@8344
reference: forbidden
steps:
  - hidden room entered: world == 0 and room not in (0, 42, 47, 48, 49, 50, 51)
  - 1-Up collected: lives == 5
  - 1-2 goal game: world == 0 and room == 42
  - back in the W1 hub: world == 0 and room == 0
forbid:
  - lost a life: lives < 4
---
A "showcase a secret" task. All you know about the secret is what the online guides say: read
`knowledge/secrets.md` ("1-2: the hidden doorway in the final cave") first. No existing movie visits it.

The movie starts from a verified library prefix: the w12-sonnet trace from power-on to the first frame of 1-2's
water cave (room 50, frame 8,344: no ability, HP 39 of 47, 4 lives). The stage's last area, the switchback cave,
is room 51; the stage's known rooms are 47-51. From there, in this order:
1. find and enter the hidden doorway (the hidden room's id is unknown: any room other than 47-51);
2. collect the 1-Up inside (lives go from 4 to 5);
3. clear 1-2 (goal game, room 42) and return to the hub.

No life may be lost. HP is 39 (one hit taken already): each further hit costs 8.

Report the cost per step and what the driver card got wrong or lacked.

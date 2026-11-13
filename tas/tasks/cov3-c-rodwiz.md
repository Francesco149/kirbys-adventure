---
name: cov3-c-rodwiz
start: main:8-wizard-fight
reference: forbidden
steps:
  - Star Rod on the ground against Nightmare: room == 16 and ability == 24
  - run to the left edge: room == 16 and ability == 24 and x < 60
  - run to the right edge: room == 16 and ability == 24 and x > 220
  - still holding the rod after the Select press, crouches, slides and floats: room == 16 and ability == 24 and frame > 135800
forbid:
  - lost a life: lives < 8
---
Coverage movie for Kirby's Star Rod states on the ground (kirby_form 6) in Nightmare's wizard fight: crouch and
slide (Down, Down+A), run into the screen edges, jump from a run and from a skid, float and press B, Select.

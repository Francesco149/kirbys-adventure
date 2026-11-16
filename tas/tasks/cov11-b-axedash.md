---
name: cov11-b-axedash
start: main@72033
reference: forbidden
steps:
  - in room 292 (low byte 36, world 4) the dashing axe knight of the top lane (type $33, slot 9, state variable 3 = 6 e33_st_dash) has dashed left across the screen to the left edge, still facing left (variable 4 = $C0): world == 4 and room == 36 and ram[0x6128+9] == 0x33 and ram[0x6200+9] == 6 and ram[0x6212+9] == 0xC0 and ram[0x6086+9]*256 + ram[0x6074+9] < 8
  - its next dash leaves the screen, e3x_clamp answers the left edge and 27:AD0A puts it at x 0 and turns it (variable 4 = $40): world == 4 and room == 36 and ram[0x6128+9] == 0x33 and ram[0x6200+9] == 6 and ram[0x6212+9] == 0x40 and ram[0x6086+9]*256 + ram[0x6074+9] < 8
forbid:
  - lost a life: lives < 6
---
Coverage movie (batch 11, part B; unit en27). The ambush of room 292 sends three dashing axe knights (type $33
variant 1, e33_dash): each faces the middle once and then dashes ~18 px every ~60 frames in the same direction. main
beats them on the way; here Kirby keeps clear of them (one hit) for ~860 frames while the top-lane knight crosses
the whole screen. Its dash past the left edge makes e3x_clamp answer the edge, and e33_st_dash's never-run side
27:AD0A-27:AD1D runs (X from e33_st_tab_tail, $90C8 turns it, $84DB / $84E6): the knight stands at x 0 and dashes
back to the right.

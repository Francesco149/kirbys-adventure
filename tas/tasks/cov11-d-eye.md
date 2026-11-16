---
name: cov11-d-eye
start: cov9-b-kracko@59600
reference: forbidden
steps:
  - Kracko's eye (slot 15, type $3D) comes back from a charge to state 9 (variable 3 = 10) while Kirby is on the floor: room == 11 and ram[0x6128+15] == 0x3D and ram[0x620F] == 10 and ram[0x05E1] < 3
  - Kirby has not floated, so variable 6 is not negative and e3d_st_after resets the eye to state 0 (2F:A3EC): room == 11 and ram[0x6128+15] == 0x3D and ram[0x620F] == 0 and ram[0x6245] < 0x80 and ram[0x05E1] < 3 and frame > 59700
  - later, in a watch state, the eye's random number is 0 on a 16-frame check with Kirby above it (not below) and within 16 px in X, so e3d_near answers carry set and variable 5 becomes $80 (2F:A1F8 / 2F:A592 falls through; the next e3d_watch takes 2F:A1A3's fall-through): room == 11 and ram[0x6128+15] == 0x3D and ram[0x6224+15] == 0x80 and ram[0x620F] < 3
forbid:
  - lost a life: lives < 4
  - hurt: hp < 15
---
Coverage movie (batch 11, part D; units cov9, en2f). The start of the Kracko fight of cov9-b-kracko, played on as
UFO Kirby. When the eye returns from its first charge to state 9 Kirby stands on the floor (in cov9 he had floated),
so e3d_st_after's variable-6 test falls through (2F:A3EC: variables 4 and 5 = 0, state 0). About 1,400 frames later,
in a watch state with UFO Kirby flying 75 px above the eye (which is below the screen then) and within 16 px of it in X, a 16-frame check draws $078C = 0 and e3d_near answers carry set
(2F:A1FA: variable 5 = $80), and the following e3d_watch calls take the negative-variable-5 path (2F:A1A5). The inputs
were found with random macro sequences checked against the branch targets on the instrumented core.

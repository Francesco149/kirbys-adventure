---
name: cov11-d-kracko
start: cov9-b-kracko@62380
reference: forbidden
steps:
  - Kracko (slot 15, type $3D) picks an attack in its pick-1 stage (e3d_pick1 calls e3d_choose) while Kirby floats high (kirby_action $0D, Y below $61): row $10 of e3d_choices, attack 1 (2F:A97C, 2F:A986): room == 11 and ram[0x6128+15] == 0x3D and ram[0x05E1] == 13 and ram[0x6099] < 0x61 and ram[0x0785] == 2 and ram[0x0784] == 1 and ram[0x078A] == 1
  - a later choice, with Kirby not floating and right of X $50 on side 1, gives attack 3 right after an attack 3, so e3d_pick1 draws attack 1 or 2 instead (2F:A9F5, 2F:B11A): room == 11 and ram[0x6128+15] == 0x3D and ram[0x05E1] != 13 and ram[0x6075] >= 0x50 and ram[0x0786] == 1 and ram[0x0784] == 3 and ram[0x078A] == 2 and ram[0x0785] == 3
  - a third choice with Kirby floating low (Y $61 or more) on side 1 (e3d_choose_1's floating path 2F:A9DB): room == 11 and ram[0x6128+15] == 0x3D and ram[0x05E1] == 13 and ram[0x6099] >= 0x61 and ram[0x0786] == 1 and ram[0x0784] == 1 and ram[0x078A] == 3 and ram[0x0785] == 3
forbid:
  - lost a life: lives < 4
  - hurt: hp < 15
---
Coverage movie (batch 11, part D; unit cov9). cov9-b-kracko reached Kracko's pick-1 stage once and chose with Kirby
standing. Continuing that fight without the UFO, Kirby floats high at the first choice (e3d_choose's floating row
$10, 2F:A97C/A986: attack 1), stands right of the middle at a later choice that comes after an attack 3 (e3d_choose_1
2F:A9F5 gives 3 again, so e3d_pick1 takes 2F:B11A and draws attack 2 from e3d_pick_alt), and floats low at a third
(e3d_choose_1's floating path 2F:A9DB, attack 3). The inputs were found with random macro sequences checked against the
branch targets on the instrumented core.

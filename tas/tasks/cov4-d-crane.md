---
name: cov4-d-crane
start: cov-minigame-crane@3940
reference: forbidden
steps:
  - first credit, the claw holds the big doll with a perfect grab (quality 0): ram[0x07BB] == 2 and ram[0x07BC] == 1 and ram[0x61CC] == 0
  - second credit, the claw holds the far doll with grab quality 1: ram[0x07BB] == 1 and ram[0x07BC] == 1 and ram[0x61CC] == 1 and ram[0x6077] >= 0x68
  - the doll slips out of the claw on the way home: ram[0x07BB] == 1 and ram[0x07BC] == 0 and ram[0x61CC] == 1 and ram[0x6076] < 185
  - back in the World 1 hub with the big doll's two lives: room == 0 and world == 0 and lives == 6
forbid:
  - lost a life: lives < 4
---
Coverage movie (units leftovers, minigame, scr_scn). Crane Fever in World 1 (level 0) from the corpus' frame before
the first credit. The first credit stops the claw exactly over the big doll (X $6B): grab quality 0, crane_tick_result's
never-run result 0 (3B:B834) and the doll's crane_side 0 path. The second credit stops the claw 4 pixels left of the
far small doll (X $C4): quality 1, so crane_tick_doll_home's random drop test runs while the doll is right of X $68 and
the doll falls (3B:B946, the claw's picture 3B:B8CB, crane_tick_carry's $07C5 end 3B:B4B5).

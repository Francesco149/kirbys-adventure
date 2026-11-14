---
name: cov5-g-ddd
start: cov4-a-ddd@130810
reference: forbidden
steps:
  - back in the 7-7 ring after the lost life, King Dedede in slot 10, Kirby in normal form with full HP: room == 14 and ram[0x6128+10] == 71 and hp == 47 and lives == 7
  - his inhale (tick e47_tick_inhale 2D.A90B) catches Kirby while Kirby is lower than him (Kirby's Y at least 2 below his): room == 14 and ram[0x6288] == 0x0B and ram[0x629A] == 0xA9 and ram[0x621C] != 0 and y >= ram[0x60AA+10]*256 + ram[0x6098+10] + 2
forbid:
  - lost another life: lives < 7
  - dying: hp > 47
---
Coverage movie (cov5, unit boss_cov3 / boss_cov4). In the corpus Dedede's inhale always caught Kirby above his
mouth, so e47_pull_vel's Y velocity was always upward. Here, from cov4-a-ddd after its lost life, Kirby is caught
standing on the floor below that point: the downward pull (2D:B49B-B4AE, the Y velocity negated) and its limit
test (2D:B4B7-B4C3; the boss's world Y + 2 against Kirby's) run, and e47_kirby_pull's Y step with it (2D:B439). On the
way a puff of e47_puff with Dedede facing right flies left (e47_puff_place, 2D:AFE2: X velocity -$0200).

---
name: cov7-k-turtle
start: cov4-a-turtle@53899
reference: forbidden
steps:
  - the 4-4 mid-boss with the round shell (type $4B, slot 10) in room 2 after cov4-a-turtle, its variable 4 = 2: room == 2 and ram[0x6128+10] == 75 and ram[0x621C] == 2
  - a grab in the open middle of the floor (no wall within 40 pixels either side), and e4b_throw_kind's random answer 1 (variable 4 = 1): room == 2 and ram[0x6128+10] == 75 and ram[0x621C] == 1 and ram[0x6086+10]*256 + ram[0x6074+10] >= 272 and ram[0x6086+10]*256 + ram[0x6074+10] <= 368
  - a second open grab whose random number below 4 meets variable 4 = 1, so the answer is 2 instead: room == 2 and ram[0x6128+10] == 75 and ram[0x621C] == 2 and ram[0x6086+10]*256 + ram[0x6074+10] >= 272 and ram[0x6086+10]*256 + ram[0x6074+10] <= 368 and hp == 15
  - a third open grab with a random number of 4 or 5 meeting variable 4 = 2: the answer 3: room == 2 and ram[0x6128+10] == 75 and ram[0x621C] == 3 and hp == 7
forbid:
  - lost a life: lives < 4
  - dying: hp > 47
---
Coverage movie (cov7, unit boss_cov3). e4b_throw_kind picks the throw after the turtle's grab; with no wall within
the six points (-40 to +40 pixels at its Y) it draws random 8 and avoids repeating variable 4. In the corpus only one
open grab happened (cov4-a-turtle@53319, answer 1). Here, from the end of cov4-a-turtle, Kirby (still holding the
UFO's star) lets the turtle grab him three times in the open part of the floor (search-driven): answer 1 (old path),
then a number below 4 that meets variable 4 = 1 (29:AB54-AB56: answer 2), then 4 or 5 meeting variable 4 = 2
(29:AB5C-AB65: answer 3). The movie stops before the third throw lands (Kirby has 7 hit points left).

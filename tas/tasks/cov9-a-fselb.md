---
name: cov9-a-fselb
start: main@60
reference: forbidden
steps:
  - the file list is up (slot 0 is the file-select object $69, state 2 = fsel_menu's list): ram[0x6128] == 0x69 and ram[0x626C] == 2 and frame < 110
  - B on the file list sends it to state $0A (fsel_back_tab, fsel_back_title): ram[0x6128] == 0x69 and ram[0x626C] == 10
  - the box is lowered and the title is back; Start opens the file select again (state 1, fsel_open): ram[0x626C] == 1 and frame > 200
  - and the file list is up again: ram[0x626C] == 2 and frame > 240
---
Coverage movie (batch 9, part A). From main at the title, before Start: the title's own ABT is left out, the file
select box rises (state 1, fsel_open) and stands as the file list (state 2, set by fsel_menu; every movie passes
through it), where B (joypad_new $40) makes fsel_input return carry set with A = 1 and fsel_tick takes
fsel_back_tab[0] = $0A: fsel_back_title lowers the box (fsel_lower, split_step_back) and title_reenter shows the
title again. No movie had pressed B there. Start then opens the file select a second time.

---
name: cov4-d-rematch
start: cov2-save-finished@152730
reference: forbidden
steps:
  - first V.S. BOSS! game, Kirby (no spare lives) beaten by the first boss: ram[0xF4] == 2 and lives == 0 and hp == 255 and room == 8
  - the game ended by itself and the title is back (game_state_init): lives == 4 and hp == 47 and ram[0xF4] == 0
  - file select, Delete Saved Game, the hand on the empty file 3: ram[0x626C] == 6 and ram[0x6248] == 2
  - ARE YOU SURE? for file 1, the hand on Yes: ram[0x626C] == 7 and ram[0x6248] == 6
  - Left puts it back on No: ram[0x626C] == 7 and ram[0x6248] == 5
  - No chosen, the file list again: ram[0x626C] == 2
  - second V.S. BOSS! game: ram[0xF4] == 2 and lives == 0 and hp == 47 and room == 8
  - Kirby beaten again: ram[0xF4] == 2 and lives == 0 and hp == 255
  - after the GAME OVER card skipped with A, the title again: lives == 4 and hp == 47 and ram[0xF4] == 0
---
Coverage movie (units scenes, scenes3). The boss rematch (V.S. BOSS!, $F4 = 2, no spare life) from the corpus' finished
file. Kirby is beaten by the first boss: the game over's gameover_skip_test sees bit 1 of $F4 and ends as GAME END by
itself (2E:A55F). Back in the file select: Delete Saved Game, A on an empty file (fsel_input's clear-carry exit
3D:B323), file 1 chosen to delete, Right to Yes and Left back to No (3D:B360), No. Then V.S. BOSS! again, Kirby is
beaten again and A is pressed on the GAME OVER card (gameover_tick_wait with bit 1 of $F4: GAME END at once, 2E:A57A).

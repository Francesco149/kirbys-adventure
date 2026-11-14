---
name: cov5-f-del
start: cov5-f-sw:fsel100
reference: forbidden
steps:
  - the file select after the reset, file 1 at 100%: world == 0 and ram[0x7905] == 63 and ram[0x7906] == 8
  - file 1 continued (CONTINUE of the finished file's menu): Kirby in the World 5 hub with the file still at 100%: room == 4 and world == 4 and ram[0x7905] == 63 and lives == 4
  - 5-1's first room entered: room == 17 and world == 4 and ram[0x055F] == 1
  - back in the World 5 hub by EXIT STAGE, the 100% file saved again: room == 4 and world == 4 and ram[0x7905] == 63
---
Coverage movie (cov5, units scenes / scenes3: the 100% file at the file select and in save_game). From cov5-f-sw's
file select with file 1 at 100%: the cursor goes to Delete Saved Game, A opens the delete screen, whose row for file 1
reads "Delete 100%" (fsel_del_rows' 100% path, 3D:B4B5), QUIT goes back; file 1 is chosen, CONTINUE puts Kirby in the
World 5 hub, he enters 5-1 and leaves by the pause screen's EXIT STAGE: save_game runs on a file whose byte 2 is
already 63 (3D:BD61-BD68, $F5 = 1). About 239,500 frames (see cov5-f-sw about the 200,000-frame limit).

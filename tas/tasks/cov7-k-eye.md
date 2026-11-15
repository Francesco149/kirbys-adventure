---
name: cov7-k-eye
start: main@59560
reference: forbidden
steps:
  - in Kracko's climb (room 11) main's UFO Kirby with the eye (type $3D) in slot 15: room == 11 and ram[0x6128+15] == 0x3D
  - the eye went 120 frames and more without a charge, and at its next draw the number was below 8 while Kirby was in the air: variable 5 put back to $20 instead of a charge (seen one frame later as $21, $078C below 8): room == 11 and ram[0x6128+15] == 0x3D and ram[0x6224+15] == 0x21 and ram[0x078C] < 8
forbid:
  - lost a life: lives < 4
  - dying: hp > 47
---
Coverage movie (cov7, unit en2f). e3d_watch decides the eye's charges: from variable 5 = $78 on, each draw (every 16
frames) of 8 or more starts a charge while Kirby is not standing; a number below 8 puts variable 5 back to $20 and
the eye waits again (2F:A1D9-A1DE). In the corpus every draw at $78 or more started the charge. Here main's UFO Kirby
flies about the bottom of the climb (search-driven) until the eye's late draw is below 8.

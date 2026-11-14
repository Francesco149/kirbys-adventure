---
name: cov5-g-kracko
start: main@59530
reference: forbidden
steps:
  - in Kracko's climb (room 11) main's Kirby is the UFO (kirby_form $0D) with the eye in slot 15: room == 11 and ram[0x6128+15] == 0x3D and ram[0x5E0] == 0x0D
  - the eye (type $3D, slot 15) starts a charge (state 4) while Kirby stands on the floor (Y velocity 0), so e3d_charge_start keeps a row-aligned Y and sets variable 8: room == 11 and ram[0x6200+15] == 4 and ram[0x625A+15] == 1 and vy == 0
forbid:
  - lost a life: lives < 4
---
Coverage movie (cov5, unit en2f). e3d_charge_start asks kirby_floor_test1; in every call of the corpus Kirby's Y
velocity was not 0 (main's UFO flies up the climb). Here main's UFO Kirby stays on the bottom floor of the climb (a Select press
at the start does not drop the UFO here) and sits still on it, Y velocity 0, when the eye decides to charge: the floor path runs (2F:A5D5-A5EA: the Y kept
for the dash is moved to a row of 8 plus $0F, variable 8 = 1) and with it the random change of the charge's
direction (2F:A601-A610: -16, -8, 8 or 16 from 2F:A614).

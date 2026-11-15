---
name: cov7-k-wiz
start: main@135120
reference: forbidden
steps:
  - the last boss's second form (type $4E, slot 9) with the Star Rod: room == 16 and ability == 24 and ram[0x6128+9] == 78
  - its first swoop (tick routine e4e_tick_swoop, 29:B5AA) starts toward the right half where Kirby was: room == 16 and ram[0x6299]*256 + ram[0x6287] == 0xB5AA and ram[0x61E5] < 0x80
  - Kirby has run left under it: the swoop ends at the right edge (screen X 208) with Kirby 112 pixels or more away, and the wizard waits there (tick 3E:D786): room == 16 and ram[0x6299]*256 + ram[0x6287] == 0xD786 and (ram[0x608F]*256 + ram[0x607D]) - (ram[0xDE]*256 + ram[0xDD]) >= 208 and abs((ram[0x608F]*256 + ram[0x607D]) - x) >= 112
  - Kirby fights on with the rod until the wizard has 8 hit points left: room == 16 and ram[0x6128+9] == 78 and ram[0x61D3] == 8
forbid:
  - lost a life: lives < 8
  - dying: hp > 47
---
Coverage movie (cov7, unit en29, also kst17). The Nightmare wizard fight from main's frame 135,120. Kirby walks into
the right half before the first swoop, so the wizard swoops right; during the swoop Kirby holds Left and passes under
it, so when the wizard reaches the screen's right edge Kirby is more than $70 pixels away: e4e_tick_swoop's far path
(29:B5D9-B5DB, entry 4 of e4e_scripts, the script 29:B261 that waits instead of turning) runs for the first time.
Then Kirby fights with the Star Rod (search-driven) and brings the wizard from 50 to 8 hit points; on the way the
rod's dive runs paths no movie had (kirby_st_rod_dive 17:A4C7-A4C9 and rod_dive_rec 17:A5CC-A5F5).

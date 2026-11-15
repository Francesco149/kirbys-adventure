---
name: cov9-a-theend
start: cov2-save-finished@149300
reference: forbidden
steps:
  - THE END is on screen (room 18): room == 18 and frame < 149400
  - still THE END 10,000 frames later, no button pressed: room == 18 and frame > 159300
  - a thread of THE END's stars runs in the_end_twinkle* (2E:BA00-BA63): room == 18 and ((ram[0x63a0] == 0xBA and ram[0x6380] < 0x64 and ram[0x63c0] == 0x2E) or (ram[0x63a1] == 0xBA and ram[0x6381] < 0x64 and ram[0x63c1] == 0x2E) or (ram[0x63a2] == 0xBA and ram[0x6382] < 0x64 and ram[0x63c2] == 0x2E) or (ram[0x63a3] == 0xBA and ram[0x6383] < 0x64 and ram[0x63c3] == 0x2E) or (ram[0x63a4] == 0xBA and ram[0x6384] < 0x64 and ram[0x63c4] == 0x2E) or (ram[0x63a5] == 0xBA and ram[0x6385] < 0x64 and ram[0x63c5] == 0x2E) or (ram[0x63a6] == 0xBA and ram[0x6386] < 0x64 and ram[0x63c6] == 0x2E) or (ram[0x63a7] == 0xBA and ram[0x6387] < 0x64 and ram[0x63c7] == 0x2E) or (ram[0x63a8] == 0xBA and ram[0x6388] < 0x64 and ram[0x63c8] == 0x2E) or (ram[0x63a9] == 0xBA and ram[0x6389] < 0x64 and ram[0x63c9] == 0x2E) or (ram[0x63aa] == 0xBA and ram[0x638a] < 0x64 and ram[0x63ca] == 0x2E) or (ram[0x63ab] == 0xBA and ram[0x638b] < 0x64 and ram[0x63cb] == 0x2E) or (ram[0x63ac] == 0xBA and ram[0x638c] < 0x64 and ram[0x63cc] == 0x2E) or (ram[0x63ad] == 0xBA and ram[0x638d] < 0x64 and ram[0x63cd] == 0x2E) or (ram[0x63ae] == 0xBA and ram[0x638e] < 0x64 and ram[0x63ce] == 0x2E) or (ram[0x63af] == 0xBA and ram[0x638f] < 0x64 and ram[0x63cf] == 0x2E))
forbid:
  - the screen changed: frame > 149310 and room != 18
---
Coverage movie (batch 9, part A). From cov2-save-finished just before THE END (the finished file's ending, room 18):
no button for about 10,500 frames. The three stars of THE END blink in the_end_sparkle, ten rounds of 255 blinks of
4 frames (10,200 frames); then the sparkle returns (the_end_sparkle_ret) and the stars go on to the_end_twinkle /
the_end_twinkle2 (the_end_blink, the_end_twinkle_a, the_end_twinkle_b and their rests) for ever. Nothing ends the
screen in that time. Thread program counters: $6380 (low), $63A0 (high), $63C0 (bank).

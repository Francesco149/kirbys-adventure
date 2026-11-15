---
name: cov9-a-w7card
start: cov4-d-w7@130900
reference: forbidden
steps:
  - World 7's card (the scene before the last fight) is still running in room 14: room == 14 and trans == 5 and frame < 130950
  - played out with no button, the card ends and the last fight begins (room 15): room == 15 and frame > 132500 and frame < 132600
  - Kirby holds the Star Rod (ability $18): room == 15 and ability == 24
  - Start in the last fight opens the pause screen (scroll_mode $051E = 7, set by pause_open) with the Star Rod's text: room == 15 and ability == 24 and ram[0x051E] == 7
  - Start again, back in the fight with the Star Rod: room == 15 and ability == 24 and ram[0x051E] != 7 and frame > 133200
forbid:
  - lost a life: lives < 8
---
Coverage movie (batch 9, part A). From cov4-d-w7's end (World 7's level card, King Dedede and Kirby before the
Fountain of Dreams, where that movie stopped) with no button for 2200 frames: the rest of the scene
(w7card_kirby_rest, w7card_dedede_rest with w7card_back / w7card_wobble, w7card_flash, w7card_part4, w7card_orb with
w7card_fade and w7card_palette: the sky darkens, the dark ball rises off the fountain), lvcard_done and the last
fight in space (room 15), where Kirby is given the Star Rod (ability 24). Start there opens the pause screen with
the STAR ROD text (pause_text_star_rod, "Make the final effort! ..."): pausing is allowed in the last fight. Start
again resumes.

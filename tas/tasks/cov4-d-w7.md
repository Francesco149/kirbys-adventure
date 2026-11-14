---
name: cov4-d-w7
start: main@130300
reference: forbidden
steps:
  - the Level 8 card (The Fountain of Dreams) plays out without a button, and 150 frames after the corpus had skipped it (it was in room 15 at frame 130449) the game is still in room 14: world == 7 and room == 14 and frame >= 130600
---
Coverage movie (unit scenes2). World 7's card from the main movie's frame before it, with no button pressed: the
card's tick pans the camera (w7card_tick 36:A6FF-36:A720, never run because every corpus movie skipped the card on its
first tick) and the scripted scene after it plays (w7card_step and the code after w7card_pad).

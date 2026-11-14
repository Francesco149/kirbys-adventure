---
name: cov4-d-story
start: attract@7300
reference: forbidden
steps:
  - A pressed on a story page, the story ends and the title comes back without its music ($07F3 set by story_skip): ram[0x07F3] == 1 and frame < 7320
---
Coverage movie (unit scenes2). The attract loop's story pages from the corpus' attract movie, with A pressed on the
first story frame: story_skip's path (36:ADF4: variable 0 of slot 0, title_long_wait = 0, $07F3 = 1, the fade-out
script 36:AD3B) and the title again.

---
name: cov6-songs
start: cov6-j-x:soundtest
reference: forbidden
steps:
  - song 1 (never started before) playing in the sound test: ram[0x07E8] == 1 and ram[0x07EA] == 1
  - song $34 (never started before) playing: ram[0x07E8] == 0x34 and ram[0x07EA] == 1
  - the last song $39 started and stopped with B: ram[0x07E8] == 0x39 and ram[0x07EA] == 0 and frame > 433600
---
Coverage movie (cov6, units sound / snddata / cov6_extra). From the sound test of cov6-j-x (the Extra Game finished,
file 1's LISTEN TO SOUNDS), every song number 0-$39 is started with A on the MUSIC row and stopped with B before the
next (A starts a song only while $07EA is 0, and only B clears it: cov6-j-x pressed A without B, so only song 0
played there). The 13 songs no movie had started (1, 2, 4, $10, $12, $1C, $1F, $21, $26, $29, $2B, $33, $34) play for
1,500 frames each, the others for 120. Scripted input from the checkpoint, no search.

---
name: cov3-c-rod
start: main:8-orb-ready
reference: forbidden
steps:
  - Star Rod shot held (the repeat shot): ability == 24 and room == 15 and ram[0x6201] >= 5
  - the orb fight runs out and the camera reaches the fountain: room == 15 and ram[0xE1]*256 + ram[0xE0] >= 0x35D
  - Kirby lost to the orb: lives == 7 and room == 15
forbid:
  - left the orb fight: room != 15
---
Coverage movie for the Star Rod flight against Nightmare's orb. Hold B so the shot repeats (rodfly_fire_test
counting to 10), then dodge without shooting until the timer runs out and the camera sinks to $035D: the flight
takes its never-run exit (script $EC) and Kirby loses a life; the orb's top test (cam_y >= $030A) answers too.

---
name: cov3-c-wade
start: cov2-water:none_in
reference: forbidden
steps:
  - mouth full out of the water: room == 45 and ram[0x5E0] == 1 and y < 140
  - walking under water with the mouth full: room == 45 and ram[0x5E0] == 1 and y >= 150 and x > 470 and x < 600
  - the mouthful spat out under water: room == 45 and ram[0x5E0] == 0 and mouth == 255 and y >= 150 and frame > 13600
forbid:
  - lost a life: lives < 4
---
Coverage movie for Kirby walking under water with his mouth full (kirby_s_full_wade, kirby_st_full_wade). In
1-1's last area Kirby inhales the enemy over the pond, drops into the water with it, walks into both banks,
stops, jumps and spits the star under water.

#!/bin/sh
# Build the instrumented FCEUmm core (stock nixpkgs libretro.fceumm + kd.patch) -> ./result, and link the
# cc65 assembler -> ./cc65 (out-links, not in git).
# The nixpkgs revision is pinned: the corpus RAM hashes were recorded on the core it builds (the stock core of
# tas/README.md comes from the same revision).
set -e
cd "$(dirname "$0")"
PIN=github:NixOS/nixpkgs/1c89083e451e891152365b799595cf7790a43325
NIXPKGS=$(nix eval --raw $PIN#path)
nix build --impure --out-link result --expr "
  let pkgs = import $NIXPKGS {};
  in pkgs.libretro.fceumm.overrideAttrs (o: { patches = (o.patches or []) ++ [ $PWD/kd.patch ]; })"
nix build $PIN#cc65 --out-link cc65
ls -l result/lib/retroarch/cores/fceumm_libretro.so cc65/bin/ca65

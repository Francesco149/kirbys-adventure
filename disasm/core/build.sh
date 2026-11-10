#!/bin/sh
# Build the instrumented FCEUmm core (stock nixpkgs libretro.fceumm + kd.patch) -> ./result, and link the
# cc65 assembler -> ./cc65 (out-links, not in git).
# The nixpkgs revision is the one the stock core (tas/core-fceumm) was built from: --inputs-from /opt/src/nix-lab.
set -e
cd "$(dirname "$0")"
NIXPKGS=$(nix eval --raw --inputs-from /opt/src/nix-lab nixpkgs#path 2>/dev/null)
nix build --impure --out-link result --expr "
  let pkgs = import $NIXPKGS {};
  in pkgs.libretro.fceumm.overrideAttrs (o: { patches = (o.patches or []) ++ [ $PWD/kd.patch ]; })"
nix build --inputs-from /opt/src/nix-lab nixpkgs#cc65 --out-link cc65
ls -l result/lib/retroarch/cores/fceumm_libretro.so cc65/bin/ca65

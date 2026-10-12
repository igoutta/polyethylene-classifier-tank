#!/usr/bin/env bash
# Compila e instala libhx711 (C++), que necesita el paquete Python hx711-rpi-py.
# Ejecutar en la Raspberry Pi antes de `uv sync --extra scale`.
set -euo pipefail

sudo apt-get update
sudo apt-get install -y build-essential git liblgpio-dev

build_dir="$(mktemp -d)"
trap 'rm -rf "$build_dir"' EXIT

git clone --depth=1 https://github.com/endail/hx711 "$build_dir/hx711"
make -C "$build_dir/hx711"
sudo make -C "$build_dir/hx711" install
sudo ldconfig

if ldconfig -p | grep -q libhx711; then
    echo "libhx711 instalada correctamente"
else
    echo "ERROR: libhx711 no aparece en ldconfig" >&2
    exit 1
fi

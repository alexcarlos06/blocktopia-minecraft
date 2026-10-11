
#!/usr/bin/env python3
"""Gerador da Fortaleza dos Herois - Blocktopia."""

import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--x", type=int, required=True)
parser.add_argument("--y", type=int, required=True)
parser.add_argument("--z", type=int, required=True)
args = parser.parse_args()

from buildings.engine import BuildingEngine

X, Y, Z = args.x, args.y, args.z

engine = BuildingEngine(X, Y, Z)

fill = engine.fill
block = engine.block

# 1. Fundacao e piso
fill(-7, -1, -7, 7, -1, 7, "stone_bricks")
fill(-6, 0, -6, 6, 0, 6, "spruce_planks")

# 2. Preparar o interior
fill(-6, 1, -6, 6, 8, 6, "air")

# 3. Paredes externas
fill(-7, 1, -7, 7, 5, -7, "stone_bricks")
fill(-7, 1, 7, 7, 5, 7, "stone_bricks")
fill(-7, 1, -6, -7, 5, 6, "stone_bricks")
fill(7, 1, -6, 7, 5, 6, "stone_bricks")

# 4. Pilares nos cantos
for dx in (-7, 7):
    for dz in (-7, 7):
        fill(dx, 1, dz, dx, 7, dz, "spruce_log")

# 5. Telhado medieval em camadas
fill(-8, 6, -8, 8, 6, 8, "spruce_planks")
fill(-6, 7, -6, 6, 7, 6, "spruce_planks")
fill(-4, 8, -4, 4, 8, 4, "spruce_planks")
fill(-2, 9, -2, 2, 9, 2, "spruce_planks")

# 6. Entrada principal ao sul
fill(-1, 1, 7, 1, 3, 7, "air")

# 7. Caminho de entrada
fill(-1, 0, 8, 1, 0, 11, "cobblestone")

# 8. Janelas
fill(-4, 3, -7, -2, 4, -7, "glass")
fill(2, 3, -7, 4, 4, -7, "glass")
fill(-7, 3, -3, -7, 4, -1, "glass")
fill(7, 3, 1, 7, 4, 3, "glass")

# 9. Iluminacao
for dx in (-5, 5):
    for dz in (-5, 5):
        block(dx, 1, dz, "sea_lantern")

# 10. Utilidades
block(-4, 1, -4, "crafting_table")
block(-3, 1, -4, "furnace")
block(-2, 1, -4, "smoker")
block(3, 1, -4, "anvil")

# 11. Baus de tesouros
block(-4, 1, 3, "chest")
block(4, 1, 3, "chest")

# 12. Marcadores externos
block(-5, 1, 9, "glowstone")
block(5, 1, 9, "glowstone")

output = engine.export(
    Path(__file__).resolve().parent
    / "buildings/generated/hero-base.commands.txt"
)

commands = engine.commands

print("Fortaleza dos Herois")
print(f"Centro: {X}, {Y}, {Z}")
print(f"Comandos gerados: {len(commands)}")
print(f"Arquivo: {output}")
print("Nenhuma alteracao foi executada no mundo.")

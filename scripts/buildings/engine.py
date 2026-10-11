#!/usr/bin/env python3
"""Motor reutilizável de construções do Blocktopia."""

import re
from pathlib import Path


class BuildingEngine:
    MAX_FILL_BLOCKS = 32768
    BLOCK_PATTERN = re.compile(r"^[a-z0-9_]+(?::[a-z0-9_]+)?$")

    def __init__(self, x: int, y: int, z: int):
        if any(type(v) is not int for v in (x, y, z)):
            raise ValueError("Coordenadas devem ser inteiras")

        self.origin = (x, y, z)
        self.commands = []
        self._bounds = None

    def _position(self, x, y, z):
        if any(type(v) is not int for v in (x, y, z)):
            raise ValueError("Coordenadas relativas devem ser inteiras")

        ox, oy, oz = self.origin
        return ox + x, oy + y, oz + z

    def _block(self, material):
        if not isinstance(material, str):
            raise ValueError("Material inválido")

        material = material.lower()

        if not self.BLOCK_PATTERN.fullmatch(material):
            raise ValueError(f"Material inválido: {material}")

        if ":" not in material:
            material = f"minecraft:{material}"

        return material

    def _record_bounds(self, start, end):
        low = tuple(min(a, b) for a, b in zip(start, end))
        high = tuple(max(a, b) for a, b in zip(start, end))

        if self._bounds is None:
            self._bounds = low + high
            return

        old_low = self._bounds[:3]
        old_high = self._bounds[3:]

        merged_low = tuple(
            min(a, b) for a, b in zip(old_low, low)
        )
        merged_high = tuple(
            max(a, b) for a, b in zip(old_high, high)
        )

        self._bounds = merged_low + merged_high

    @property
    def bounds(self):
        """Limites absolutos: minX,minY,minZ,maxX,maxY,maxZ."""
        return self._bounds

    @property
    def dimensions(self):
        """Dimensões em blocos: largura, altura, profundidade."""
        if self._bounds is None:
            return None

        x1, y1, z1, x2, y2, z2 = self._bounds
        return (x2 - x1 + 1, y2 - y1 + 1, z2 - z1 + 1)

    @property
    def footprint(self):
        """Retângulo X/Z que contém todos os comandos."""
        if self._bounds is None:
            return None

        x1, _, z1, x2, _, z2 = self._bounds
        return (x1, z1, x2, z2)

    def fill(self, a, b, c, d, e, f, material):
        start = self._position(a, b, c)
        end = self._position(d, e, f)

        volume = (
            (abs(d - a) + 1)
            * (abs(e - b) + 1)
            * (abs(f - c) + 1)
        )

        if volume > self.MAX_FILL_BLOCKS:
            raise ValueError(
                f"Fill excede limite de {self.MAX_FILL_BLOCKS} blocos"
            )

        coords = " ".join(map(str, start + end))
        command = f"fill {coords} {self._block(material)}"

        self._record_bounds(start, end)
        self.commands.append(command)
        return command

    def block(self, x, y, z, material):
        px, py, pz = self._position(x, y, z)

        command = (
            f"setblock {px} {py} {pz} "
            f"{self._block(material)}"
        )

        self._record_bounds((px, py, pz), (px, py, pz))
        self.commands.append(command)
        return command

    def export(self, path):
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)

        output.write_text(
            "\n".join(self.commands) + "\n",
            encoding="utf-8"
        )

        return output

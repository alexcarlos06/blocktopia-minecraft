"""Inspeção conservadora de volumes de construções no Blocktopia."""

from collections import Counter

from scripts.terrain.materials import (
    MaterialCategory,
    classify_material,
)


class VolumeAnalyzer:
    MAX_BLOCKS = 100000

    def __init__(self, reader):
        self.reader = reader

    def analyze(self, bounds):
        if (
            not isinstance(bounds, tuple)
            or len(bounds) != 6
            or any(type(value) is not int for value in bounds)
        ):
            raise ValueError("Limites tridimensionais inválidos")

        x1, y1, z1, x2, y2, z2 = bounds

        if x1 > x2 or y1 > y2 or z1 > z2:
            raise ValueError("Limites invertidos")

        volume = (
            (x2 - x1 + 1)
            * (y2 - y1 + 1)
            * (z2 - z1 + 1)
        )

        if volume > self.MAX_BLOCKS:
            raise ValueError("Volume excede limite de segurança")

        categories = Counter()
        occupied = 0
        unknown = 0
        empty = 0

        for x in range(x1, x2 + 1):
            for z in range(z1, z2 + 1):
                for y in range(y1, y2 + 1):
                    # Erros de leitura são propagados intencionalmente.
                    block = self.reader.get_block(x, y, z)

                    if block is None:
                        unknown += 1
                        continue

                    category = classify_material(block)
                    categories[category.value] += 1

                    if category == MaterialCategory.AIR:
                        empty += 1
                    else:
                        occupied += 1

        return {
            "status": "PENDENTE",
            "bounds": bounds,
            "total_blocks": volume,
            "empty_blocks": empty,
            "occupied_blocks": occupied,
            "unknown_blocks": unknown,
            "material_categories": dict(categories),
            "reason": (
                "Inspeção geométrica concluída; aprovação "
                "de construção ainda não implementada."
            ),
        }

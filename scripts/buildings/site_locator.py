"""Busca preliminar de locais para aventuras do Blocktopia.

Não modifica o mundo e não autoriza construções.
"""

from math import hypot


class SiteLocator:
    MAX_CANDIDATES_SCANNED = 5000

    def __init__(self, reader):
        self.reader = reader

    def find(
        self,
        reference,
        footprint_size,
        min_distance,
        max_distance,
        step=16,
        limit=5,
    ):
        if (
            not isinstance(reference, (tuple, list))
            or len(reference) != 2
            or any(type(v) is not int for v in reference)
        ):
            raise ValueError("Referência X/Z inválida")

        if (
            not isinstance(footprint_size, (tuple, list))
            or len(footprint_size) != 2
            or any(type(v) is not int or not 1 <= v <= 64
                   for v in footprint_size)
        ):
            raise ValueError("Dimensões inválidas")

        if (
            type(min_distance) is not int
            or type(max_distance) is not int
            or not 0 <= min_distance <= max_distance <= 2000
        ):
            raise ValueError("Distâncias inválidas")

        if type(step) is not int or not 1 <= step <= 64:
            raise ValueError("Passo inválido")

        if type(limit) is not int or not 1 <= limit <= 20:
            raise ValueError("Limite inválido")

        rx, rz = reference
        width, depth = footprint_size
        midpoint = (min_distance + max_distance) / 2

        candidates = []
        scanned = 0

        # X/Z representam o canto inicial do terreno candidato.
        for dx in range(-max_distance, max_distance + 1, step):
            for dz in range(-max_distance, max_distance + 1, step):
                x = rx + dx
                z = rz + dz

                center_x = x + (width - 1) / 2
                center_z = z + (depth - 1) / 2

                distance = hypot(center_x - rx, center_z - rz)

                if not min_distance <= distance <= max_distance:
                    continue

                scanned += 1
                if scanned > self.MAX_CANDIDATES_SCANNED:
                    raise ValueError(
                        "Busca excedeu limite de candidatos; "
                        "reduza a distância ou aumente o passo"
                    )

                heights = []

                for cx in range(x, x + width):
                    for cz in range(z, z + depth):
                        height = self.reader.get_height(cx, cz)
                        if height is None:
                            continue
                        if type(height) is not int:
                            raise ValueError(
                                "Altura de terreno inválida"
                            )
                        if not -64 <= height <= 319:
                            raise ValueError(
                                "Altura fora dos limites Bedrock"
                            )
                        heights.append(height)

                total = width * depth

                # Não sugerir área com dados incompletos.
                if len(heights) != total:
                    continue

                slope = max(heights) - min(heights)
                base_y = max(heights) + 1

                if base_y > 319:
                    continue

                # Menor desnível primeiro; distância como desempate.
                score = (
                    slope,
                    abs(distance - midpoint),
                    x,
                    z,
                )

                candidates.append({
                    "status": "PENDENTE",
                    "execution_allowed": False,
                    "x": x,
                    "z": z,
                    "suggested_y": base_y,
                    "footprint": (
                        x, z, x + width - 1, z + depth - 1
                    ),
                    "distance": round(distance, 2),
                    "min_height": min(heights),
                    "max_height": max(heights),
                    "slope": slope,
                    "score": score,
                    "warning": (
                        "Local preliminar baseado somente em alturas "
                        "estimadas. Verificar obstáculos, construções, "
                        "materiais e volume no Bedrock antes de construir."
                    ),
                })

        candidates.sort(key=lambda item: item["score"])

        return {
            "status": "PENDENTE",
            "execution_allowed": False,
            "reference": tuple(reference),
            "footprint_size": tuple(footprint_size),
            "distance_range": (min_distance, max_distance),
            "scanned": scanned,
            "candidates": candidates[:limit],
        }

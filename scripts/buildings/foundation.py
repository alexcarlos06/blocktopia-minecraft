"""Planejamento de fundações do Blocktopia, sem executar comandos."""

from enum import Enum


class FoundationStrategy(str, Enum):
    NATURAL = "NATURAL"
    LEVEL = "LEVEL"
    ELEVATED = "ELEVATED"


class FoundationPlanner:
    MAX_COLUMNS = 10000

    def __init__(self, reader):
        self.reader = reader

    def plan(self, footprint, base_y, strategy="NATURAL"):
        if (
            not isinstance(footprint, tuple)
            or len(footprint) != 4
            or any(type(v) is not int for v in footprint)
        ):
            raise ValueError("Footprint inválido")

        x1, z1, x2, z2 = footprint

        if x1 > x2 or z1 > z2:
            raise ValueError("Limites invertidos")

        if type(base_y) is not int:
            raise ValueError("Altura da base inválida")

        try:
            strategy = FoundationStrategy(strategy)
        except (ValueError, TypeError) as exc:
            raise ValueError("Estratégia inválida") from exc

        total = (x2 - x1 + 1) * (z2 - z1 + 1)

        if total > self.MAX_COLUMNS:
            raise ValueError("Área excede limite de análise")

        columns = []
        known_heights = []

        for z in range(z1, z2 + 1):
            for x in range(x1, x2 + 1):
                height = self.reader.get_height(x, z)

                if height is not None:
                    if type(height) is not int:
                        raise ValueError("Altura de terreno inválida")
                    known_heights.append(height)

                columns.append({
                    "x": x,
                    "z": z,
                    "ground_y": height,
                })

        # ELEVATED posiciona a base acima do maior solo conhecido.
        # Com dados ausentes, essa elevação é apenas provisória.
        target_y = base_y

        if strategy == FoundationStrategy.ELEVATED and known_heights:
            target_y = max(base_y, max(known_heights) + 1)

        excavation = 0
        foundation = 0
        unknown = 0

        for column in columns:
            ground = column["ground_y"]

            if ground is None:
                unknown += 1
                column["excavation_blocks"] = None
                column["foundation_blocks"] = None
                continue

            cut = 0
            fill = 0

            if strategy == FoundationStrategy.LEVEL:
                # Libera o espaço a partir da base planejada.
                cut = max(0, ground - target_y + 1)
                # Sustenta a base até Y=target_y-1.
                fill = max(0, target_y - ground - 1)

            elif strategy == FoundationStrategy.ELEVATED:
                fill = max(0, target_y - ground - 1)

            column["excavation_blocks"] = cut
            column["foundation_blocks"] = fill

            excavation += cut
            foundation += fill

        return {
            "status": "PENDENTE",
            "strategy": strategy.value,
            "footprint": footprint,
            "original_base_y": base_y,
            "suggested_base_y": target_y,
            "elevation": target_y - base_y,
            "total_columns": total,
            "known_columns": len(known_heights),
            "unknown_columns": unknown,
            "coverage_percent": round(
                len(known_heights) * 100 / total, 2
            ),
            "min_height": (
                min(known_heights) if known_heights else None
            ),
            "max_height": (
                max(known_heights) if known_heights else None
            ),
            "excavation_blocks": excavation,
            "foundation_blocks": foundation,
            "columns": columns,
            "commands": [],
            "warning": (
                "Plano preliminar: alturas Data3D estimadas. "
                "Escavações, materiais, sustentação e regiões "
                "desconhecidas exigem revisão antes da execução."
            ),
        }

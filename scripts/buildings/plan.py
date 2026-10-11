"""Integra fundação e estrutura, sem executar comandos."""

from scripts.buildings.foundation import FoundationPlanner
from scripts.buildings.foundation_commands import (
    generate_foundation_commands,
)


class BuildingPlan:
    MIN_Y = -64
    MAX_Y = 319

    def __init__(
        self,
        building,
        reader,
        foundation_strategy="NATURAL",
        foundation_material="cobblestone",
    ):
        self.building = building
        self.reader = reader
        self.foundation_strategy = foundation_strategy
        self.foundation_material = foundation_material

    @classmethod
    def _check_y(cls, y):
        if not cls.MIN_Y <= y <= cls.MAX_Y:
            raise ValueError(
                f"Altura Y={y} fora dos limites Bedrock"
            )

    @classmethod
    def _shift_command(cls, command, offset):
        """Desloca somente comandos gerados pelo BuildingEngine."""

        parts = command.split()

        if parts[0:1] == ["setblock"] and len(parts) == 5:
            x, y, z = map(int, parts[1:4])
            y += offset
            cls._check_y(y)

            return f"setblock {x} {y} {z} {parts[4]}"

        if parts[0:1] == ["fill"] and len(parts) == 8:
            x1, y1, z1, x2, y2, z2 = map(
                int, parts[1:7]
            )
            y1 += offset
            y2 += offset

            cls._check_y(y1)
            cls._check_y(y2)

            return (
                f"fill {x1} {y1} {z1} "
                f"{x2} {y2} {z2} {parts[7]}"
            )

        raise ValueError(
            f"Comando de construção não suportado: {command}"
        )

    def generate(self):
        building = self.building

        if (
            building is None
            or building.bounds is None
            or building.footprint is None
            or not building.commands
        ):
            raise ValueError("Construção vazia ou inválida")

        original_bounds = building.bounds
        original_base_y = original_bounds[1]

        foundation_report = FoundationPlanner(
            self.reader
        ).plan(
            footprint=building.footprint,
            base_y=original_base_y,
            strategy=self.foundation_strategy,
        )

        target_y = foundation_report["suggested_base_y"]
        offset = target_y - original_base_y

        foundation_result = generate_foundation_commands(
            foundation_report,
            material=self.foundation_material,
        )

        structure_commands = [
            self._shift_command(command, offset)
            for command in building.commands
        ]

        x1, y1, z1, x2, y2, z2 = original_bounds
        self._check_y(y1 + offset)
        self._check_y(y2 + offset)

        adjusted_bounds = (
            x1, y1 + offset, z1,
            x2, y2 + offset, z2,
        )

        foundation_commands = foundation_result["commands"]

        return {
            "status": "PENDENTE",
            "execution_allowed": False,
            "strategy": foundation_report["strategy"],
            "original_bounds": original_bounds,
            "adjusted_bounds": adjusted_bounds,
            "original_base_y": original_base_y,
            "suggested_base_y": target_y,
            "elevation": offset,
            "terrain_coverage_percent": (
                foundation_report["coverage_percent"]
            ),
            "known_columns": (
                foundation_report["known_columns"]
            ),
            "unknown_columns": (
                foundation_report["unknown_columns"]
            ),
            "excavation_blocks": (
                foundation_report["excavation_blocks"]
            ),
            "foundation_blocks": (
                foundation_report["foundation_blocks"]
            ),
            "foundation_commands": foundation_commands,
            "structure_commands": structure_commands,
            "commands": (
                foundation_commands + structure_commands
            ),
            "warning": (
                "Plano preliminar. Alturas do terreno são "
                "estimadas. Nenhuma execução foi autorizada."
            ),
        }

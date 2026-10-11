"""Prévia consolidada de construções Blocktopia.

Somente análise. Não executa comandos Minecraft.
"""

from types import SimpleNamespace

from scripts.buildings.plan import BuildingPlan
from scripts.buildings.validator import BuildingValidator


def generate_building_preview(
    building,
    reader,
    foundation_strategy="NATURAL",
    foundation_material="cobblestone",
):
    """Gera plano e diagnóstico considerando a posição final."""

    plan = BuildingPlan(
        building=building,
        reader=reader,
        foundation_strategy=foundation_strategy,
        foundation_material=foundation_material,
    ).generate()

    bounds = plan["adjusted_bounds"]

    # Adapta somente os limites para validar a posição final.
    # Não modifica o BuildingEngine original.
    adjusted_building = SimpleNamespace(
        bounds=bounds,
        footprint=(bounds[0], bounds[2], bounds[3], bounds[5]),
    )

    validation = BuildingValidator(reader).validate(
        adjusted_building
    )

    terrain = validation["terrain"]
    volume = validation["volume"]

    return {
        "status": "PENDENTE",
        "execution_allowed": False,
        "strategy": plan["strategy"],
        "original_bounds": plan["original_bounds"],
        "adjusted_bounds": bounds,
        "original_base_y": plan["original_base_y"],
        "suggested_base_y": plan["suggested_base_y"],
        "elevation": plan["elevation"],
        "foundation": {
            "known_columns": plan["known_columns"],
            "unknown_columns": plan["unknown_columns"],
            "coverage_percent": plan["terrain_coverage_percent"],
            "excavation_blocks": plan["excavation_blocks"],
            "foundation_blocks": plan["foundation_blocks"],
            "command_count": len(plan["foundation_commands"]),
        },
        "terrain": {
            "min_height": terrain["min_height"],
            "max_height": terrain["max_height"],
            "height_difference": terrain["height_difference"],
            "overhead_obstacles": terrain["overhead_obstacles"],
            "missing_positions": terrain["missing_positions"],
        },
        "volume": {
            "total_blocks": volume["total_blocks"],
            "occupied_blocks": volume["occupied_blocks"],
            "unknown_blocks": volume["unknown_blocks"],
        },
        "structure_command_count": len(
            plan["structure_commands"]
        ),
        "total_commands": len(plan["commands"]),
        "blockers": validation["blockers"],
        "commands": plan["commands"],
        "warning": (
            "Prévia baseada em alturas estimadas. "
            "A validação da estrutura não substitui a revisão "
            "dos comandos de preparação da fundação. "
            "Nenhum comando foi executado."
        ),
    }

"""Coordenação conservadora das validações de construção do Blocktopia."""

from scripts.terrain.analyzer import TerrainAnalyzer
from scripts.terrain.volume_analyzer import VolumeAnalyzer
from scripts.terrain.building_validation import validate_building_position


class BuildingValidator:
    """Produz diagnósticos, mas ainda não autoriza construções."""

    def __init__(self, reader, inspection_height=4):
        self.terrain_analyzer = TerrainAnalyzer(
            reader,
            inspection_height=inspection_height,
        )
        self.volume_analyzer = VolumeAnalyzer(reader)

    def validate(self, building):
        if (
            building is None
            or building.bounds is None
            or building.footprint is None
        ):
            raise ValueError("Construção vazia ou inválida")

        terrain = self.terrain_analyzer.analyze(
            building.footprint
        )

        position = validate_building_position(
            building.bounds,
            terrain,
        )

        volume = self.volume_analyzer.analyze(
            building.bounds
        )

        blockers = []

        if terrain["missing_positions"] > 0:
            blockers.append("ALTURAS_AUSENTES")

        if terrain["unreadable_material_positions"] > 0:
            blockers.append("MATERIAIS_ILEGIVEIS")

        if terrain["unknown_overhead_positions"] > 0:
            blockers.append("DADOS_SUPERIORES_AUSENTES")

        if terrain["overhead_obstacles"] > 0:
            blockers.append("OBSTACULOS_SUPERIORES")

        if volume["unknown_blocks"] > 0:
            blockers.append("VOLUME_INCOMPLETO")

        if volume["occupied_blocks"] > 0:
            blockers.append("VOLUME_OCUPADO")

        # Esta versão é exclusivamente de diagnóstico.
        blockers.append("CRITERIOS_DE_APROVACAO_PENDENTES")

        return {
            "status": "PENDENTE",
            "execution_allowed": False,
            "bounds": building.bounds,
            "footprint": building.footprint,
            "terrain": terrain,
            "position": position,
            "volume": volume,
            "blockers": blockers,
        }

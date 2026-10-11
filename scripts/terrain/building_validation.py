"""Avaliação preliminar da relação entre construção e terreno."""


def validate_building_position(bounds, terrain_report):
    """Compara a base planejada com as alturas disponíveis."""

    if (
        not isinstance(bounds, tuple)
        or len(bounds) != 6
        or any(type(value) is not int for value in bounds)
    ):
        raise ValueError("Limites da construção inválidos")

    x1, y1, z1, x2, y2, z2 = bounds

    if x1 > x2 or y1 > y2 or z1 > z2:
        raise ValueError("Limites da construção invertidos")

    expected_footprint = (x1, z1, x2, z2)

    if terrain_report["footprint"] != expected_footprint:
        raise ValueError("Área analisada diferente da construção")

    ground_min = terrain_report["min_height"]
    ground_max = terrain_report["max_height"]

    if (
        terrain_report["missing_positions"] > 0
        or ground_min is None
        or ground_max is None
    ):
        return {
            "status": "PENDENTE",
            "building_base": y1,
            "building_top": y2,
            "ground_min": ground_min,
            "ground_max": ground_max,
            "reason": "Dados de altura incompletos.",
        }

    return {
        "status": "PENDENTE",
        "building_base": y1,
        "building_top": y2,
        "ground_min": ground_min,
        "ground_max": ground_max,
        "maximum_excavation": max(0, ground_max - y1),
        "maximum_foundation": max(0, y1 - ground_min),
        "reason": (
            "Estimativa preliminar de escavação e fundação. "
            "Validação tridimensional ainda pendente."
        ),
    }

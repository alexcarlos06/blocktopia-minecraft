#!/usr/bin/env python3
"""Analisador preliminar de terreno do Blocktopia."""

from collections import Counter

from scripts.terrain.materials import classify_material


class TerrainAnalyzer:
    MAX_POSITIONS = 10000

    def __init__(self, reader):
        self.reader = reader

    def analyze(self, footprint):
        """Analisa um retângulo X/Z, sem alterar o mundo."""

        if (
            not isinstance(footprint, tuple)
            or len(footprint) != 4
            or any(type(value) is not int for value in footprint)
        ):
            raise ValueError("Footprint inválido")

        x1, z1, x2, z2 = footprint

        if x1 > x2 or z1 > z2:
            raise ValueError("Limites do footprint invertidos")

        width = x2 - x1 + 1
        depth = z2 - z1 + 1
        total = width * depth

        if total > self.MAX_POSITIONS:
            raise ValueError(
                f"Área excede o limite de {self.MAX_POSITIONS} posições"
            )

        heights = []
        missing = []
        materials = Counter()
        unreadable_materials = []

        for z in range(z1, z2 + 1):
            for x in range(x1, x2 + 1):
                # Erros de leitura devem interromper a análise.
                # Apenas ausência explícita é registrada como desconhecida.
                height = self.reader.get_height(x, z)

                if height is None:
                    missing.append((x, z))
                else:
                    if type(height) is not int:
                        raise ValueError(
                            f"Altura inválida em X={x}, Z={z}"
                        )
                    heights.append(height)

                    # Inspeciona apenas o bloco na altura estimada.
                    # Erros de leitura bloqueiam a análise.
                    block = self.reader.get_block(x, height, z)

                    if block is None:
                        unreadable_materials.append((x, height, z))
                    else:
                        category = classify_material(block)
                        materials[category.value] += 1

        minimum = min(heights) if heights else None
        maximum = max(heights) if heights else None

        return {
            "status": "PENDENTE",
            "footprint": footprint,
            "width": width,
            "depth": depth,
            "total_positions": total,
            "available_positions": len(heights),
            "missing_positions": len(missing),
            "missing_coordinates": missing,
            "material_categories": dict(materials),
            "unreadable_material_positions": len(
                unreadable_materials
            ),
            "unreadable_material_coordinates": unreadable_materials,
            "min_height": minimum,
            "max_height": maximum,
            "height_difference": (
                maximum - minimum
                if heights else None
            ),
            "reason": (
                "Dados incompletos; validação de materiais e "
                "obstáculos ainda não implementada."
                if missing else
                "Alturas disponíveis; validação de materiais e "
                "obstáculos ainda não implementada."
            ),
        }

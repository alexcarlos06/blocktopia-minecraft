"""Classificação conservadora de materiais do Blocktopia."""

from enum import Enum


class MaterialCategory(str, Enum):
    GROUND = "SOLO"
    LIQUID = "LIQUIDO"
    VEGETATION = "VEGETACAO"
    SNOW_LAYER = "NEVE_SUPERFICIAL"
    AIR = "AR"
    UNKNOWN = "DESCONHECIDO"


KNOWN_MATERIALS = {
    MaterialCategory.GROUND: {
        "minecraft:grass_block",
        "minecraft:dirt",
        "minecraft:stone",
        "minecraft:deepslate",
        "minecraft:andesite",
        "minecraft:granite",
        "minecraft:diorite",
        "minecraft:sand",
        "minecraft:gravel",
        "minecraft:coarse_dirt",
        "minecraft:podzol",
        "minecraft:snow",
    },
    MaterialCategory.LIQUID: {
        "minecraft:water",
        "minecraft:flowing_water",
        "minecraft:lava",
        "minecraft:flowing_lava",
    },
    MaterialCategory.VEGETATION: {
        "minecraft:short_grass",
        "minecraft:tall_grass",
        "minecraft:cornflower",
        "minecraft:dandelion",
        "minecraft:poppy",
        "minecraft:oak_leaves",
        "minecraft:oak_log",
        "minecraft:spruce_leaves",
        "minecraft:spruce_log",
    },
    MaterialCategory.SNOW_LAYER: {
        "minecraft:snow_layer",
    },
    MaterialCategory.AIR: {
        "minecraft:air",
        "minecraft:cave_air",
    },
}


MATERIAL_INDEX = {
    material: category
    for category, materials in KNOWN_MATERIALS.items()
    for material in materials
}


def classify_material(material):
    """Classifica um material; dados inesperados ficam desconhecidos."""

    if not isinstance(material, str):
        return MaterialCategory.UNKNOWN

    return MATERIAL_INDEX.get(
        material.lower(),
        MaterialCategory.UNKNOWN,
    )

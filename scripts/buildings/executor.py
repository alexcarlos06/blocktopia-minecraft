"""Validação e simulação de comandos de construção do Blocktopia.

Não acessa Docker, não envia comandos e não altera o mundo.
"""

import re


class BuildingExecutor:
    MIN_Y = -64
    MAX_Y = 319
    MAX_FILL_BLOCKS = 32768
    MAX_COMMANDS = 1000

    MATERIAL = re.compile(
        r"(?:minecraft:)?[a-z0-9_]+"
    )

    @classmethod
    def validate_command(cls, command):
        if not isinstance(command, str):
            raise ValueError("Comando deve ser texto")

        parts = command.split()

        if not parts or parts[0] not in ("fill", "setblock"):
            raise ValueError("Comando não autorizado")

        if parts[0] == "setblock":
            if len(parts) != 5:
                raise ValueError("Sintaxe setblock inválida")

            coordinates = parts[1:4]
            material = parts[4]

        else:
            if len(parts) != 8:
                raise ValueError("Sintaxe fill inválida")

            coordinates = parts[1:7]
            material = parts[7]

        if not cls.MATERIAL.fullmatch(material):
            raise ValueError("Material inválido")

        if not all(re.fullmatch(r"-?\d+", c) for c in coordinates):
            raise ValueError("Coordenadas inválidas")

        numbers = list(map(int, coordinates))

        if parts[0] == "setblock":
            volume = 1
            heights = [numbers[1]]
        else:
            x1, y1, z1, x2, y2, z2 = numbers
            volume = (
                (abs(x2 - x1) + 1)
                * (abs(y2 - y1) + 1)
                * (abs(z2 - z1) + 1)
            )
            heights = [y1, y2]

            if volume > cls.MAX_FILL_BLOCKS:
                raise ValueError(
                    "Comando fill excede 32768 blocos"
                )

        if any(
            y < cls.MIN_Y or y > cls.MAX_Y
            for y in heights
        ):
            raise ValueError("Altura fora dos limites Bedrock")

        return {
            "command": command,
            "type": parts[0],
            "volume": volume,
        }

    def dry_run(self, preview):
        if not isinstance(preview, dict):
            raise ValueError("Prévia inválida")

        commands = preview.get("commands")

        if not isinstance(commands, list) or not commands:
            raise ValueError("Lista de comandos vazia ou inválida")

        if len(commands) > self.MAX_COMMANDS:
            raise ValueError("Quantidade de comandos excedida")

        if preview.get("total_commands") != len(commands):
            raise ValueError("Quantidade de comandos inconsistente")

        foundation_count = preview.get("foundation", {}).get(
            "command_count"
        )
        structure_count = preview.get("structure_command_count")

        if (
            type(foundation_count) is not int
            or type(structure_count) is not int
            or foundation_count < 0
            or structure_count < 1
            or foundation_count + structure_count != len(commands)
        ):
            raise ValueError("Composição do plano inconsistente")

        validated = [
            self.validate_command(command)
            for command in commands
        ]

        return {
            "status": "DRY_RUN",
            "execution_allowed": False,
            "command_count": len(validated),
            "foundation_commands": foundation_count,
            "structure_commands": structure_count,
            "total_command_volume": sum(
                item["volume"] for item in validated
            ),
            "terrain_coverage_percent": preview["foundation"][
                "coverage_percent"
            ],
            "unknown_columns": preview["foundation"][
                "unknown_columns"
            ],
            "blockers": list(preview.get("blockers", [])),
            "commands": [item["command"] for item in validated],
            "warning": (
                "Simulação apenas. O volume informado é a soma "
                "dos volumes dos comandos, não a quantidade "
                "de blocos distintos efetivamente alterados."
            ),
        }

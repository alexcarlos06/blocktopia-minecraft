"""Geração de comandos Bedrock para preparação do terreno.

Não executa comandos e não altera o mundo.
"""


def generate_foundation_commands(report, material="cobblestone"):
    if not isinstance(report, dict):
        raise ValueError("Relatório inválido")

    strategy = report.get("strategy")
    if strategy not in ("NATURAL", "LEVEL", "ELEVATED"):
        raise ValueError("Estratégia inválida")

    target_y = report.get("suggested_base_y")
    if type(target_y) is not int:
        raise ValueError("Altura da base inválida")

    if not -64 <= target_y <= 319:
        raise ValueError("Base fora dos limites de altura suportados")

    if not isinstance(material, str) or not material:
        raise ValueError("Material inválido")

    # Evita inserir argumentos extras nos comandos Bedrock.
    if not all(c.islower() or c.isdigit() or c == "_"
               for c in material):
        raise ValueError("Nome de material inválido")

    columns = report.get("columns")
    if not isinstance(columns, list):
        raise ValueError("Colunas inválidas")

    if len(columns) > 10000:
        raise ValueError("Quantidade de colunas excedida")

    commands = []
    skipped = 0

    for column in columns:
        if not isinstance(column, dict):
            raise ValueError("Coluna inválida")

        x = column.get("x")
        z = column.get("z")
        ground = column.get("ground_y")

        if type(x) is not int or type(z) is not int:
            raise ValueError("Coordenadas inválidas")

        if ground is None:
            skipped += 1
            continue

        if type(ground) is not int or not -64 <= ground <= 319:
            raise ValueError("Altura do solo inválida")

        if strategy == "NATURAL":
            continue

        if strategy == "LEVEL" and ground >= target_y:
            commands.append(
                f"fill {x} {target_y} {z} "
                f"{x} {ground} {z} air"
            )

        if ground < target_y - 1:
            commands.append(
                f"fill {x} {ground + 1} {z} "
                f"{x} {target_y - 1} {z} {material}"
            )

    return {
        "strategy": strategy,
        "commands": commands,
        "command_count": len(commands),
        "unknown_columns_skipped": skipped,
        "execution_allowed": False,
        "warning": (
            "Comandos preliminares. Revisar terreno, "
            "estimativas de altura e possíveis estruturas "
            "antes de autorizar qualquer execução."
        ),
    }

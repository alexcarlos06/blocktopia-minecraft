"""Política simples de autorização de construções do Blocktopia.

Este módulo decide se há autorização administrativa.
Não executa comandos no Minecraft.
"""

from enum import Enum


class ExecutionMode(str, Enum):
    DRY_RUN = "DRY_RUN"
    STRICT = "STRICT"
    FORCE = "FORCE"


def authorize_building(
    validation,
    mode=ExecutionMode.DRY_RUN,
    admin_confirmed=False,
):
    """Avalia a autorização sem executar a construção."""

    if not isinstance(validation, dict):
        raise ValueError("Relatório de validação inválido")

    try:
        mode = ExecutionMode(mode)
    except (ValueError, TypeError) as exc:
        raise ValueError("Modo de execução inválido") from exc

    bounds = validation.get("bounds")
    blockers = validation.get("blockers")

    if (
        not isinstance(bounds, tuple)
        or len(bounds) != 6
        or any(type(value) is not int for value in bounds)
    ):
        raise ValueError("Limites da construção inválidos")

    x1, y1, z1, x2, y2, z2 = bounds

    if x1 > x2 or y1 > y2 or z1 > z2:
        raise ValueError("Limites da construção invertidos")

    if (
        not isinstance(blockers, list)
        or any(not isinstance(b, str) for b in blockers)
    ):
        raise ValueError("Lista de bloqueios inválida")

    if type(admin_confirmed) is not bool:
        raise ValueError("Confirmação administrativa inválida")

    result = {
        "mode": mode.value,
        "authorized": False,
        "bounds": bounds,
        "blockers": list(blockers),
    }

    if mode == ExecutionMode.DRY_RUN:
        result["message"] = "Simulação: execução desabilitada"
        return result

    if mode == ExecutionMode.STRICT:
        result["authorized"] = (
            validation.get("status") == "APROVADO"
            and validation.get("execution_allowed") is True
            and not blockers
        )
        result["message"] = (
            "Validação aprovada"
            if result["authorized"]
            else "Construção não aprovada pelo validador"
        )
        return result

    # FORCE: o administrador aceita os riscos informados,
    # inclusive obstáculos e regiões desconhecidas.
    if not admin_confirmed:
        result["message"] = "Confirmação do administrador necessária"
        return result

    result["authorized"] = True
    result["message"] = "Construção autorizada pelo administrador"
    return result

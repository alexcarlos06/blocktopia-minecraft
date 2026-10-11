"""Política de autorização administrativa do Blocktopia.

Este módulo não executa comandos Minecraft.
"""

from enum import Enum


class ExecutionMode(str, Enum):
    DRY_RUN = "DRY_RUN"
    STRICT = "STRICT"
    MANUAL_OVERRIDE = "MANUAL_OVERRIDE"


DATA_BLOCKERS = {
    "ALTURAS_AUSENTES",
    "MATERIAIS_ILEGIVEIS",
    "DADOS_SUPERIORES_AUSENTES",
    "VOLUME_INCOMPLETO",
}

KNOWN_CONFLICTS = {
    "VOLUME_OCUPADO",
    "OBSTACULOS_SUPERIORES",
}


def authorize_building(
    validation,
    mode=ExecutionMode.DRY_RUN,
    admin_confirmed=False,
    reason=None,
):
    """Avalia a autorização, sem executar a construção."""

    if not isinstance(validation, dict):
        raise ValueError("Relatório de validação inválido")

    try:
        mode = ExecutionMode(mode)
    except ValueError as exc:
        raise ValueError("Modo de execução inválido") from exc

    blockers = validation.get("blockers")

    if (
        not isinstance(blockers, list)
        or any(not isinstance(b, str) for b in blockers)
    ):
        raise ValueError("Bloqueios inválidos")

    blockers = set(blockers)

    if not isinstance(admin_confirmed, bool):
        raise ValueError("Confirmação administrativa inválida")

    unknown_blockers = (
        blockers
        - DATA_BLOCKERS
        - KNOWN_CONFLICTS
        - {"CRITERIOS_DE_APROVACAO_PENDENTES"}
    )

    if unknown_blockers:
        return {
            "authorized": False,
            "mode": mode.value,
            "reason": "Bloqueios não reconhecidos",
            "blockers": sorted(unknown_blockers),
        }

    if mode == ExecutionMode.DRY_RUN:
        return {
            "authorized": False,
            "mode": mode.value,
            "reason": "Modo de simulação",
            "blockers": sorted(blockers),
        }

    if mode == ExecutionMode.STRICT:
        return {
            "authorized": bool(
                validation.get("execution_allowed") is True
                and validation.get("status") == "APROVADO"
                and not blockers
            ),
            "mode": mode.value,
            "reason": "Validação automática obrigatória",
            "blockers": sorted(blockers),
        }

    if DATA_BLOCKERS & blockers:
        return {
            "authorized": False,
            "mode": mode.value,
            "reason": "Dados de terreno incompletos",
            "blockers": sorted(DATA_BLOCKERS & blockers),
        }

    if not admin_confirmed:
        return {
            "authorized": False,
            "mode": mode.value,
            "reason": "Confirmação administrativa necessária",
            "blockers": sorted(blockers),
        }

    if not isinstance(reason, str) or not reason.strip():
        return {
            "authorized": False,
            "mode": mode.value,
            "reason": "Justificativa administrativa obrigatória",
            "blockers": sorted(blockers),
        }

    if not validation.get("bounds"):
        return {
            "authorized": False,
            "mode": mode.value,
            "reason": "Limites da construção não informados",
            "blockers": sorted(blockers),
        }

    return {
        "authorized": True,
        "mode": mode.value,
        "reason": reason.strip(),
        "blockers": sorted(blockers),
        "authorization_type": "ADMINISTRATIVE_OVERRIDE",
    }

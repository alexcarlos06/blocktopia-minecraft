"""Orquestrador de construção do Blocktopia.

Primeira versão: somente um setblock por execução.
O backup é obrigatório antes do envio ao Bedrock.
"""

import re
import subprocess
import sys
from pathlib import Path

from scripts.buildings.executor import BuildingExecutor
from scripts.buildings.bedrock_sender import BedrockCommandSender


class ConstructionRunner:
    BACKUP_SCRIPT = (
        Path(__file__).resolve().parents[1]
        / "backup" / "backup-world.py"
    )
    BACKUP_DIR = Path(
        "/home/alexcsousa/projects/minecraft-backups"
    )

    def execute(
        self,
        command,
        mode="DRY_RUN",
        admin_confirmed=False,
    ):
        # Validar antes de qualquer operação externa.
        validated = BuildingExecutor.validate_command(command)

        if validated["type"] != "setblock":
            raise ValueError(
                "Esta versão aceita somente setblock"
            )

        if mode not in ("DRY_RUN", "FORCE"):
            raise ValueError("Modo inválido")

        if mode == "DRY_RUN":
            return {
                "status": "DRY_RUN",
                "command": command,
                "backup": None,
                "sent": False,
            }

        if admin_confirmed is not True:
            raise PermissionError(
                "Confirmação administrativa obrigatória"
            )

        # Fazer o backup antes de enviar qualquer comando.
        try:
            process = subprocess.run(
                [sys.executable, str(self.BACKUP_SCRIPT)],
                capture_output=True,
                text=True,
                timeout=120,
                check=True,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                "Backup excedeu o tempo limite. "
                "Nenhum comando de construção será enviado. "
                "Verifique se o salvamento foi retomado."
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                "Backup falhou. Construção cancelada. "
                + (exc.stderr or "").strip()
            ) from exc

        matches = re.findall(
            r"^BACKUP CONCLUÍDO: (.+)$",
            process.stdout,
            flags=re.MULTILINE,
        )

        if len(matches) != 1 or (
            "Salvamento do mundo retomado."
            not in process.stdout
        ):
            raise RuntimeError(
                "Conclusão do backup não confirmada"
            )

        backup = Path(matches[0].strip())

        # Aceitar somente um diretório online-* dentro do
        # local oficial de backups.
        if (
            backup.parent != self.BACKUP_DIR
            or not re.fullmatch(
                r"online-\d{8}-\d{6}", backup.name
            )
            or not backup.is_dir()
            or backup.is_symlink()
        ):
            raise RuntimeError(
                "Diretório do backup inválido"
            )

        world = backup / "worlds" / "Blocktopia"
        required = [
            world / "level.dat",
            world / "levelname.txt",
            world / "db" / "CURRENT",
        ]

        if any(
            not path.is_file() or path.is_symlink()
            for path in required
        ):
            raise RuntimeError(
                "Arquivos essenciais do backup ausentes"
            )

        # O transporte confirma o envio, não a colocação
        # efetiva do bloco no mundo.
        result = BedrockCommandSender().send_setblock(
            validated["command"],
            admin_confirmed=True,
        )

        return {
            "status": result["status"],
            "command": validated["command"],
            "backup": str(backup),
            "sent": True,
            "confirmed_in_world": False,
        }

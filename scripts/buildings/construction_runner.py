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
from scripts.buildings.bedrock_verifier import BedrockVerifier


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

        if (
            validated["type"] == "fill"
            and validated["volume"]
            > BedrockVerifier.MAX_FILL_VERIFICATION_BLOCKS
        ):
            raise ValueError(
                "Construção fill limitada a 64 blocos nesta versão"
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
        sender = BedrockCommandSender()

        if validated["type"] == "fill":
            result = sender.send_fill(
                validated["command"],
                admin_confirmed=True,
            )
        else:
            result = sender.send_setblock(
                validated["command"],
                admin_confirmed=True,
            )

        # Consultar o bloco após o envio.
        # Falha na verificação não deve reenviar a construção.
        try:
            verifier = BedrockVerifier()

            if validated["type"] == "fill":
                verification = verifier.verify_fill(
                    validated["command"]
                )
            else:
                verification = verifier.verify_setblock(
                    validated["command"]
                )
            verification_status = verification.get(
                "status", "INDETERMINADO"
            )
            if verification_status not in (
                "CONFIRMADO", "DIVERGENTE", "INDETERMINADO"
            ):
                verification_status = "INDETERMINADO"

            verification_message = verification.get(
                "message", "Sem detalhes da verificação"
            )
        except Exception as exc:
            verification_status = "INDETERMINADO"
            verification_message = (
                "Verificação falhou: "
                + type(exc).__name__
            )

        return {
            "status": result["status"],
            "command": validated["command"],
            "backup": str(backup),
            "sent": True,
            "verification_status": verification_status,
            "verification_message": verification_message,
            "confirmed_in_world": (
                verification_status == "CONFIRMADO"
            ),
        }

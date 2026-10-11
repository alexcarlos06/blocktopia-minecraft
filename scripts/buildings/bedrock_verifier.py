"""Consulta somente leitura para verificar blocos no Minecraft Bedrock."""

import re
import subprocess
import time
from datetime import datetime, timezone

from scripts.buildings.executor import BuildingExecutor
from scripts.buildings.bedrock_sender import BedrockCommandSender


class BedrockVerifier:
    CONTAINER = BedrockCommandSender.CONTAINER
    USER = BedrockCommandSender.USER
    TIMEOUT_SECONDS = 8

    def verify_setblock(self, command):
        validated = BuildingExecutor.validate_command(command)

        if validated["type"] != "setblock":
            raise ValueError("Verificação aceita somente setblock")

        _, x, y, z, material = validated["command"].split()
        query = f"testforblock {x} {y} {z} {material}"

        expected = re.compile(
            rf"Successfully found the block at "
            rf"{re.escape(str(int(x)))},"
            rf"{re.escape(str(int(y)))},"
            rf"{re.escape(str(int(z)))}\."
        )

        # Captura o instante anterior ao envio da consulta.
        since = datetime.now(timezone.utc).isoformat()

        try:
            subprocess.run(
                [
                    "docker", "exec",
                    "--user", self.USER,
                    self.CONTAINER,
                    "sh", "-c",
                    BedrockCommandSender.SEND_SCRIPT,
                    "sh", query,
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
        except (subprocess.CalledProcessError,
                subprocess.TimeoutExpired) as exc:
            return {
                "status": "INDETERMINADO",
                "confirmed_in_world": False,
                "command": query,
                "message": f"Falha ou timeout no envio da consulta: {exc}",
            }

        deadline = time.monotonic() + self.TIMEOUT_SECONDS

        while time.monotonic() < deadline:
            try:
                logs = subprocess.run(
                    [
                        "docker", "logs",
                        "--since", since,
                        "--timestamps",
                        self.CONTAINER,
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=5,
                )
            except (subprocess.CalledProcessError,
                    subprocess.TimeoutExpired) as exc:
                return {
                    "status": "INDETERMINADO",
                    "confirmed_in_world": False,
                    "command": query,
                    "message": f"Não foi possível consultar os logs: {exc}",
                }

            if expected.search(logs.stdout):
                return {
                    "status": "CONFIRMADO",
                    "confirmed_in_world": True,
                    "command": query,
                    "message": "Bloco encontrado na coordenada esperada",
                }

            time.sleep(0.5)

        return {
            "status": "INDETERMINADO",
            "confirmed_in_world": False,
            "command": query,
            "message": (
                "Resposta conclusiva não encontrada nos logs. "
                "O bloco pode existir; a consulta não conseguiu comprová-lo."
            ),
        }

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

    MAX_FILL_VERIFICATION_BLOCKS = 64

    def verify_fill(self, command):
        """Verifica cada posição de um fill, sem modificar o mundo."""
        validated = BuildingExecutor.validate_command(command)

        if validated["type"] != "fill":
            raise ValueError("Verificação aceita somente fill")

        volume = validated["volume"]
        if volume > self.MAX_FILL_VERIFICATION_BLOCKS:
            raise ValueError(
                "Verificação fill limitada a 64 blocos nesta versão"
            )

        _, x1, y1, z1, x2, y2, z2, material = (
            validated["command"].split()
        )

        x1, y1, z1, x2, y2, z2 = map(
            int, (x1, y1, z1, x2, y2, z2)
        )

        confirmed = 0
        divergent = 0
        indeterminate = 0

        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    block_command = (
                        f"setblock {x} {y} {z} {material}"
                    )

                    try:
                        result = self.verify_setblock(block_command)
                        status = result.get("status")
                    except Exception:
                        status = "INDETERMINADO"

                    if status == "CONFIRMADO":
                        confirmed += 1
                    elif status == "DIVERGENTE":
                        divergent += 1
                    else:
                        indeterminate += 1

        if divergent:
            status = "DIVERGENTE"
        elif indeterminate:
            status = "INDETERMINADO"
        else:
            status = "CONFIRMADO"

        return {
            "status": status,
            "confirmed_in_world": status == "CONFIRMADO",
            "command": validated["command"],
            "total_blocks": volume,
            "confirmed_blocks": confirmed,
            "divergent_blocks": divergent,
            "indeterminate_blocks": indeterminate,
        }

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

            # Docker pode retornar mensagens em stdout ou stderr.
            output = logs.stdout + "\n" + logs.stderr

            # Respostas observadas no Bedrock do Blocktopia:
            # Successfully found the block at 23,133,-28.
            # The block at 23,133,-29 is Stone (expected: Air).
            divergent = re.compile(
                rf"The block at "
                rf"{re.escape(str(int(x)))},"
                rf"{re.escape(str(int(y)))},"
                rf"{re.escape(str(int(z)))} "
                rf"is (.+?) [(]expected: (.+?)[)][.]"
            )

            match = divergent.search(output)

            if match:
                return {
                    "status": "DIVERGENTE",
                    "confirmed_in_world": False,
                    "command": query,
                    "found_block": match.group(1),
                    "expected_block": match.group(2),
                    "message": (
                        f"Encontrado: {match.group(1)}; "
                        f"esperado: {match.group(2)}"
                    ),
                }

            if expected.search(output):
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

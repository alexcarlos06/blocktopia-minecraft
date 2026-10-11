"""Transporte restrito de comandos de construção para o Bedrock.

O envio ao STDIN não comprova execução bem-sucedida no mundo.
"""

import subprocess

from scripts.buildings.executor import BuildingExecutor


class BedrockCommandSender:
    CONTAINER = "blocktopia"
    USER = "1001:1001"

    SEND_SCRIPT = r'''
set -eu

PID=""
COUNT=0

for proc in /proc/[0-9]*; do
    candidate="${proc##*/}"
    exe=$(readlink "$proc/exe" 2>/dev/null) || continue

    case "$exe" in
        /data/bedrock_server-*)
            PID="$candidate"
            COUNT=$((COUNT + 1))
            ;;
    esac
done

if [ "$COUNT" -ne 1 ]; then
    echo "ERRO: esperado exatamente um processo Bedrock" >&2
    exit 1
fi

if [ ! -w "/proc/$PID/fd/0" ]; then
    echo "ERRO: STDIN do Bedrock inacessível" >&2
    exit 1
fi

printf "%s\n" "$1" > "/proc/$PID/fd/0"
'''

    def send_setblock(self, command, *, admin_confirmed=False):
        """Envia somente setblock, após confirmação explícita.

        A criação e validação do backup serão responsabilidade
        do orquestrador de construções.
        """
        if admin_confirmed is not True:
            raise PermissionError(
                "Confirmação administrativa obrigatória"
            )

        validated = BuildingExecutor.validate_command(command)

        if validated["type"] != "setblock":
            raise ValueError(
                "Este transporte permite somente setblock"
            )

        try:
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "--user",
                    self.USER,
                    self.CONTAINER,
                    "sh",
                    "-c",
                    self.SEND_SCRIPT,
                    "sh",
                    validated["command"],
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                "Tempo limite no envio; resultado no Bedrock é desconhecido"
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                "Falha no envio ao console Bedrock: "
                + (exc.stderr or "").strip()
            ) from exc

        return {
            "status": "ENVIADO",
            "confirmed_in_world": False,
            "container": self.CONTAINER,
            "command": validated["command"],
            "message": (
                "Comando entregue ao console; "
                "execução no mundo ainda não verificada"
            ),
        }

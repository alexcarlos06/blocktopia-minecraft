#!/usr/bin/env bash
set -euo pipefail

CONTAINER="blocktopia"
USER_ID="1001:1001"
LOCK_FILE="/tmp/blocktopia-save-cycle.lock"

exec 9>"$LOCK_FILE"

if ! flock -n 9; then
    echo "ERRO: já existe um teste de salvamento em execução."
    exit 1
fi

send_command() {
    local command="$1"

    docker exec --user "$USER_ID" "$CONTAINER" sh -c '
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
            echo "ERRO: processo Bedrock não identificado" >&2
            exit 1
        fi

        if [ ! -w "/proc/$PID/fd/0" ]; then
            echo "ERRO: console Bedrock inacessível" >&2
            exit 1
        fi

        printf "%s\n" "$1" > "/proc/$PID/fd/0"
    ' sh "$command"
}

HOLD_ATTEMPTED=0
RESUME_SENT=0

cleanup() {
    local status=$?
    trap - EXIT INT TERM

    if [ "$HOLD_ATTEMPTED" -eq 1 ] &&
       [ "$RESUME_SENT" -eq 0 ]; then

        echo
        echo "Liberando salvamento com save resume..."

        if send_command "save resume"; then
            RESUME_SENT=1
            echo "save resume enviado."
        else
            echo "ATENÇÃO: falha ao enviar save resume!" >&2
            echo "Verifique imediatamente o console Bedrock." >&2
            status=1
        fi
    fi

    exit "$status"
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

if [ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER")" != "true" ]; then
    echo "ERRO: container não está em execução."
    exit 1
fi

SINCE="$(date +%s)"

echo "=== BLOCKTOPIA — TESTE DO CICLO SAVE ==="
echo "Container: $CONTAINER"
echo "Início: $(date '+%Y-%m-%d %H:%M:%S')"
echo

echo "Enviando save hold..."
HOLD_ATTEMPTED=1
send_command "save hold"

READY=0

for attempt in $(seq 1 10); do
    sleep 3

    echo "Consulta $attempt/10..."
    send_command "save query"

    sleep 2

    LOGS="$(docker logs --since "$SINCE" "$CONTAINER" 2>&1)"

    if grep -Fq \
      "Data saved. Files are now ready to be copied." \
      <<< "$LOGS"; then
        READY=1
        echo "Bedrock informou que os arquivos estão prontos."
        break
    fi
done

echo
echo "=== RESPOSTAS DO BEDROCK ==="
docker logs --since "$SINCE" "$CONTAINER" 2>&1 | tail -60

echo

if [ "$READY" -eq 1 ]; then
    echo "SUCESSO: preparação de backup confirmada."
else
    echo "AVISO: preparação não confirmada dentro do prazo."
fi

echo "Finalizando ciclo..."
# A rotina cleanup enviará save resume.

if [ "$READY" -ne 1 ]; then
    exit 1
fi

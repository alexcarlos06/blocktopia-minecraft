#!/usr/bin/env bash
set -euo pipefail

CONTAINER="blocktopia"
USER_ID="1001:1001"

if [ "$#" -ne 1 ] || [ "$1" != "list" ]; then
    echo "Uso nesta versão: $0 list" >&2
    exit 1
fi

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
        echo "ERRO: esperado exatamente um processo Bedrock; encontrados: $COUNT" >&2
        exit 1
    fi

    if [ ! -w "/proc/$PID/fd/0" ]; then
        echo "ERRO: STDIN do Bedrock inacessivel" >&2
        exit 1
    fi

    printf "list\n" > "/proc/$PID/fd/0"

    echo "Comando enviado ao Bedrock (PID $PID)."
'

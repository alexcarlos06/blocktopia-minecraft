#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONTAINER="blocktopia"
RULES="$BASE_DIR/config/gamerules.conf"
APPLY="$BASE_DIR/scripts/admin/apply-gamerules.sh"

last_applied=""

echo "Monitor de gamerules iniciado."

while true; do
  started=$(docker inspect \
    --format '{{if .State.Running}}{{.State.StartedAt}}{{end}}' \
    "$CONTAINER" 2>/dev/null || true)

  if [[ -z "$started" ]]; then
    sleep 5
    continue
  fi

  if [[ "$started" == "$last_applied" ]]; then
    sleep 5
    continue
  fi

  # Aguarda a mensagem de inicialização desta instância.
  ready=false

  for attempt in $(seq 1 60); do
    current=$(docker inspect \
      --format '{{if .State.Running}}{{.State.StartedAt}}{{end}}' \
      "$CONTAINER" 2>/dev/null || true)

    [[ "$current" == "$started" ]] || break

    if docker logs --since "$started" "$CONTAINER" 2>&1 \
        | grep -Fq "Server started."; then
      ready=true
      break
    fi

    sleep 5
  done

  if [[ "$ready" != true ]]; then
    echo "Servidor não ficou pronto ou reiniciou."
    sleep 5
    continue
  fi

  echo "Bedrock pronto. Aplicando gamerules..."
  issued_at=$(date +%s)

  if ! "$APPLY"; then
    echo "Falha no envio. Nova tentativa será realizada."
    sleep 10
    continue
  fi

  # Valida as respostas reais de todas as regras.
  verified=false

  for attempt in $(seq 1 15); do
    logs=$(docker logs --since "$issued_at" \
      "$CONTAINER" 2>&1 || true)

    count=0
    expected=0

    while IFS= read -r line || [[ -n "$line" ]]; do
      [[ "$line" =~ ^[[:space:]]*(#|$) ]] && continue

      read -r cmd rule value <<< "$line"
      expected=$((expected + 1))

      message="Game rule $rule has been updated to $value"

      if grep -Fq "$message" <<< "$logs"; then
        count=$((count + 1))
      fi
    done < "$RULES"

    if [[ "$expected" -eq 19 && "$count" -eq "$expected" ]]; then
      verified=true
      break
    fi

    sleep 2
  done

  current=$(docker inspect \
    --format '{{if .State.Running}}{{.State.StartedAt}}{{end}}' \
    "$CONTAINER" 2>/dev/null || true)

  if [[ "$verified" == true && "$current" == "$started" ]]; then
    echo "SUCESSO: 19 gamerules confirmadas."
    last_applied="$started"
  else
    echo "Validação incompleta. Será realizada nova tentativa."
    sleep 10
  fi
done

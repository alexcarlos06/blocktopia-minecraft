#!/usr/bin/env bash
set -euo pipefail

CONTAINER="blocktopia"
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RULES="$BASE_DIR/config/gamerules.conf"

# Regras permitidas para o Blocktopia.
ALLOWED_RULES=(
  keepinventory showcoordinates showdaysplayed
  recipesunlock showrecipemessages dolimitedcrafting
  dotiledrops doentitydrops domobloot
  dodaylightcycle doweathercycle domobspawning
  naturalregeneration dofiretick
  falldamage firedamage drowningdamage doinsomnia
  pvp
)

test -f "$RULES" || {
  echo "ERRO: arquivo não encontrado: $RULES"
  exit 1
}

test "$(docker inspect -f '{{.State.Running}}' "$CONTAINER")" = "true" || {
  echo "ERRO: container não está executando"
  exit 1
}

# Valida todo o arquivo antes de enviar qualquer comando.
COMMANDS=()

while IFS= read -r line || [[ -n "$line" ]]; do
  [[ "$line" =~ ^[[:space:]]*(#|$) ]] && continue

  if [[ ! "$line" =~ ^gamerule[[:space:]]+([a-z]+)[[:space:]]+(true|false)[[:space:]]*$ ]]; then
    echo "ERRO: sintaxe inválida: $line"
    exit 1
  fi

  rule="${BASH_REMATCH[1]}"
  allowed=false

  for item in "${ALLOWED_RULES[@]}"; do
    if [[ "$item" == "$rule" ]]; then
      allowed=true
      break
    fi
  done

  if [[ "$allowed" != true ]]; then
    echo "ERRO: gamerule não autorizada: $rule"
    exit 1
  fi

  COMMANDS+=("$line")
done < "$RULES"

echo "Aplicando ${#COMMANDS[@]} regras do Blocktopia..."

for command in "${COMMANDS[@]}"; do
  docker exec --user 1001:1001 "$CONTAINER" \
    sh -c '
      set -eu
      count=0
      for proc in /proc/[0-9]*; do
        exe=$(readlink "$proc/exe" 2>/dev/null) || continue
        case "$exe" in
          /data/bedrock_server-*)
            pid="${proc##*/}"
            count=$((count + 1))
            ;;
        esac
      done
      [ "$count" -eq 1 ] || exit 1
      [ -w "/proc/$pid/fd/0" ] || exit 1
      printf "%s\n" "$1" > "/proc/$pid/fd/0"
    ' sh "$command"

  echo "Enviado: $command"
  sleep 1
done

echo "Todos os comandos foram enviados."
echo "Valide a aplicação nos logs do Bedrock."

#!/usr/bin/env python3
"""Backup online do mundo Blocktopia via protocolo save do Bedrock."""

import fcntl
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CONTAINER = "blocktopia"
USER = "1001:1001"
DATA = Path("/home/alexcsousa/projects/minecraft-data")
BACKUPS = Path("/home/alexcsousa/projects/minecraft-backups")
WORLD = "Blocktopia"

READY = "Data saved. Files are now ready to be copied."
RESUMED = "Changes to the world are resumed."

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
[ "$COUNT" -eq 1 ] || exit 1
[ -w "/proc/$PID/fd/0" ] || exit 1
printf "%s\n" "$1" > "/proc/$PID/fd/0"
'''


def run(args):
    return subprocess.run(
        args, check=True, capture_output=True, text=True
    ).stdout


def send(command):
    run([
        "docker", "exec", "--user", USER,
        CONTAINER, "sh", "-c", SEND_SCRIPT, "sh", command
    ])


def logs(since):
    result = subprocess.run(
        ["docker", "logs", "--since", since, CONTAINER],
        capture_output=True, text=True, check=True
    )
    return result.stdout + "\n" + result.stderr


def wait_for(message, since, seconds=12):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if message in logs(since):
            return True
        time.sleep(1)
    return False


def parse_file_list(output):
    lines = output.splitlines()
    candidates = []

    for index, line in enumerate(lines):
        if READY in line and index + 1 < len(lines):
            candidates.append(lines[index + 1].strip())

    if not candidates:
        return None

    entries = {}
    line = candidates[-1]

    if not line.startswith(WORLD + "/"):
        raise ValueError("Lista de arquivos inesperada")

    for entry in line.split(", "):
        match = re.fullmatch(
            rf"({re.escape(WORLD)}/[A-Za-z0-9_.\-/]+):([0-9]+)",
            entry,
        )
        if not match:
            raise ValueError(f"Entrada de backup inválida: {entry}")

        relative = Path(match.group(1))
        size = int(match.group(2))

        if ".." in relative.parts or relative.parts[0] != WORLD:
            raise ValueError("Caminho de backup inválido")

        if relative in entries or size <= 0:
            raise ValueError("Arquivo duplicado ou tamanho inválido")

        entries[relative] = size

    required = {
        Path(f"{WORLD}/level.dat"),
        Path(f"{WORLD}/levelname.txt"),
    }

    if not required.issubset(entries):
        raise ValueError("Arquivos essenciais ausentes")

    if not any("db" in path.parts for path in entries):
        raise ValueError("Banco LevelDB não informado")

    if len(entries) > 10000:
        raise ValueError("Quantidade excessiva de arquivos")

    return entries


def copy_files(entries, target):
    source_root = DATA / "worlds"

    for relative, size in entries.items():
        source = source_root / relative
        destination = target / relative

        # Garante que a origem permanece dentro de worlds/.
        root_resolved = source_root.resolve(strict=True)
        source_resolved = source.resolve(strict=True)

        if not source_resolved.is_relative_to(root_resolved):
            raise ValueError(
                f"Arquivo fora do diretório do mundo: {relative}"
            )

        # Impede seguir links simbólicos na origem.
        metadata = source.lstat()
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError(f"Origem não é arquivo regular: {relative}")

        if metadata.st_size < size:
            raise ValueError(f"Arquivo menor que o informado: {relative}")

        destination.parent.mkdir(parents=True, exist_ok=True)

        with source.open("rb") as inp, destination.open("xb") as out:
            remaining = size
            while remaining:
                chunk = inp.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise IOError(f"Leitura incompleta: {relative}")
                out.write(chunk)
                remaining -= len(chunk)

            out.flush()
            os.fsync(out.fileno())

        if destination.stat().st_size != size:
            raise IOError(f"Tamanho incorreto: {relative}")



def handle_shutdown(signum, frame):
    """Interrompe normalmente para permitir a execução do finally."""
    raise InterruptedError(
        f"Backup interrompido pelo sinal {signum}"
    )


def main():
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    BACKUPS.mkdir(parents=True, exist_ok=True)

    with open("/tmp/blocktopia-save-cycle.lock", "a+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("Outro ciclo de backup está em execução")

        state = run([
            "docker", "inspect",
            "--format", "{{.State.Running}}", CONTAINER
        ]).strip()

        if state != "true":
            raise RuntimeError("Container blocktopia não está executando")

        mounts = run([
            "docker", "inspect", "--format",
            "{{range .Mounts}}{{println .Source \"->\" .Destination}}{{end}}",
            CONTAINER,
        ])

        expected_mount = f"{DATA} -> /data"
        if expected_mount not in mounts.splitlines():
            raise RuntimeError("Montagem /data diferente da esperada")

        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        final = BACKUPS / f"online-{stamp}"
        temporary = BACKUPS / f".online-{stamp}.partial"

        if final.exists() or temporary.exists():
            raise RuntimeError("Destino de backup já existe")

        since = datetime.now(timezone.utc).isoformat()
        hold_attempted = False
        resume_confirmed = False
        copied = False

        try:
            print("=== BACKUP ONLINE BLOCKTOPIA ===", flush=True)
            print("Enviando save hold...", flush=True)
            hold_attempted = True
            send("save hold")

            entries = None

            for attempt in range(1, 11):
                time.sleep(3)
                send("save query")
                time.sleep(1)

                entries = parse_file_list(logs(since))
                if entries:
                    break

                print(f"Aguardando Bedrock: {attempt}/10", flush=True)

            if not entries:
                raise RuntimeError("save query não retornou arquivos")

            print(f"Arquivos informados: {len(entries)}", flush=True)
            print(
                f"Bytes esperados: {sum(entries.values())}",
                flush=True,
            )

            temporary.mkdir()
            copy_files(entries, temporary / "worlds")

            copied = True
            print("Arquivos copiados e tamanhos verificados.", flush=True)

        finally:
            if hold_attempted:
                print("Enviando save resume...", flush=True)

                # A recuperação não deve ser interrompida por
                # um segundo Ctrl+C ou SIGTERM.
                signal.signal(signal.SIGINT, signal.SIG_IGN)
                signal.signal(signal.SIGTERM, signal.SIG_IGN)

                try:
                    send("save resume")
                    resume_confirmed = wait_for(RESUMED, since)
                except Exception as exc:
                    print(f"ERRO AO LIBERAR SALVAMENTO: {exc}", file=sys.stderr)

                if not resume_confirmed:
                    print(
                        "ATENÇÃO: save resume NÃO foi confirmado. "
                        "Verifique o console imediatamente.",
                        file=sys.stderr,
                    )

        if not resume_confirmed:
            raise RuntimeError("Backup não confirmado: falha no resume")

        if not copied:
            raise RuntimeError("Cópia do backup incompleta")

        temporary.rename(final)

        print(f"BACKUP CONCLUÍDO: {final}", flush=True)
        print("Salvamento do mundo retomado.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"BACKUP NÃO CONCLUÍDO: {exc}", file=sys.stderr)
        sys.exit(1)

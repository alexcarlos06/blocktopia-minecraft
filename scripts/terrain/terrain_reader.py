#!/usr/bin/env python3
"""Leitor experimental de blocos do mundo Blocktopia."""

import struct
import warnings
from pathlib import Path

import amulet_nbt
from leveldb import LevelDB


class TerrainReader:
    SUPPORTED_BITS = (1, 2, 3, 4, 5, 6, 8, 16)

    def __init__(self, world_path):
        self.world_path = Path(world_path)
        db_path = self.world_path / "db"

        if not (db_path / "CURRENT").is_file():
            raise ValueError("Banco LevelDB não encontrado")

        self.db = LevelDB(str(db_path), False)
        self.cache = {}

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _load_subchunk(self, cx, cz, sy):
        cache_key = (cx, cz, sy)

        if cache_key in self.cache:
            return self.cache[cache_key]

        if not -128 <= sy <= 127:
            raise ValueError("Índice vertical fora do formato suportado")

        key = struct.pack("<iiBb", cx, cz, 0x2F, sy)

        try:
            data = self.db.get(key)
        except KeyError:
            return None

        if len(data) < 4 or data[0] != 9 or data[1] != 1:
            raise ValueError("Formato de subchunk não suportado")

        header_y = struct.unpack_from("<b", data, 2)[0]
        if header_y != sy:
            raise ValueError("Altura do subchunk inconsistente")

        header = data[3]
        bits = header >> 1

        if header & 1:
            raise ValueError("Paleta runtime não suportada")

        if bits not in self.SUPPORTED_BITS:
            raise ValueError("Bits por bloco não suportados")

        per_word = 32 // bits
        words = (4096 + per_word - 1) // per_word
        offset = 4 + words * 4

        if offset + 4 > len(data):
            raise ValueError("Subchunk incompleto")

        count = struct.unpack_from("<I", data, offset)[0]

        if not 1 <= count <= 4096:
            raise ValueError("Quantidade de entradas inválida")

        raw = data[offset + 4:]
        palette = []
        consumed = 0

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)

            for _ in range(count):
                entry, size = amulet_nbt.load(
                    raw[consumed:],
                    compressed=False,
                    little_endian=True,
                    offset=True
                )

                if size <= 0 or consumed + size > len(raw):
                    raise ValueError("Entrada NBT inválida")

                palette.append(str(entry.tag["name"].py_str))
                consumed += size

        if consumed != len(raw):
            raise ValueError("Paleta incompleta")

        result = (data, bits, per_word, palette)
        self.cache[cache_key] = result
        return result

    def get_height(self, x: int, z: int):
        """Retorna a superfície estimada via Data3D ou None.

        A conversão foi validada em amostras do Blocktopia.
        Não deve ser usada isoladamente para aprovar construções.
        """
        if type(x) is not int or type(z) is not int:
            raise ValueError("Coordenadas devem ser inteiras")

        cx, cz = x // 16, z // 16
        lx, lz = x % 16, z % 16

        key = struct.pack("<iiB", cx, cz, 0x2B)

        try:
            data = self.db.get(key)
        except KeyError:
            return None

        if len(data) < 512:
            raise ValueError("Registro Data3D incompleto")

        index = lz * 16 + lx
        raw_height = struct.unpack_from(
            "<H", data, index * 2
        )[0]

        return raw_height - 65

    def get_block(self, x, y, z):
        """Retorna o material ou None se o subchunk estiver ausente."""

        cx, cz, sy = x // 16, z // 16, y // 16

        subchunk = self._load_subchunk(cx, cz, sy)

        if subchunk is None:
            return None

        data, bits, per_word, palette = subchunk

        lx, ly, lz = x % 16, y % 16, z % 16

        index = lx * 256 + lz * 16 + ly
        word_index = index // per_word
        shift = (index % per_word) * bits

        word = struct.unpack_from(
            "<I", data, 4 + word_index * 4
        )[0]

        palette_index = (word >> shift) & ((1 << bits) - 1)

        if palette_index >= len(palette):
            raise ValueError("Índice de paleta inválido")

        return palette[palette_index]

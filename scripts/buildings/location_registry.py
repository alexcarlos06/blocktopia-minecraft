"""Catálogo de referências das aventuras do Blocktopia.

Não acessa Docker e não modifica o mundo Minecraft.
"""

import json
import os
import re
import tempfile
from pathlib import Path


class LocationRegistry:
    ID_PATTERN = re.compile(r"[a-z][a-z0-9_]{0,63}")

    def __init__(self, path):
        self.path = Path(path)

    @classmethod
    def validate_id(cls, location_id):
        if (
            not isinstance(location_id, str)
            or not cls.ID_PATTERN.fullmatch(location_id)
        ):
            raise ValueError("Identificador de local inválido")

    @staticmethod
    def validate_coordinates(x, y, z):
        if any(type(value) is not int for value in (x, y, z)):
            raise ValueError("Coordenadas devem ser inteiras")
        if not -64 <= y <= 319:
            raise ValueError("Altura fora dos limites Bedrock")
        if not all(-(2**31) <= v < 2**31 for v in (x, z)):
            raise ValueError("Coordenadas X/Z fora dos limites")

    def load(self):
        if not self.path.is_file():
            raise FileNotFoundError(
                f"Catálogo não encontrado: {self.path}"
            )

        data = json.loads(self.path.read_text(encoding="utf-8"))

        if (
            not isinstance(data, dict)
            or data.get("version") != 1
            or not isinstance(data.get("locations"), dict)
        ):
            raise ValueError("Formato do catálogo inválido")

        return data

    def get(self, location_id):
        self.validate_id(location_id)
        return self.load()["locations"].get(location_id)

    def reference(self, location_id):
        location = self.get(location_id)

        if location is None:
            raise KeyError(f"Local não cadastrado: {location_id}")

        if location.get("status") != "CONFIRMADO":
            raise ValueError(
                f"Local ainda não confirmado: {location_id}"
            )

        x = location.get("x")
        y = location.get("y")
        z = location.get("z")
        self.validate_coordinates(x, y, z)

        return (x, z)

    def register(self, location_id, *, name, x, y, z):
        self.validate_id(location_id)
        self.validate_coordinates(x, y, z)

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Nome do local obrigatório")

        data = self.load()

        if location_id in data["locations"]:
            raise ValueError(
                "Local já cadastrado. Atualização exige revisão."
            )

        data["locations"][location_id] = {
            "name": name.strip(),
            "x": x,
            "y": y,
            "z": z,
            "status": "CONFIRMADO",
        }

        # Escrita atômica: evita arquivo JSON parcial.
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=".locations-",
                suffix=".tmp",
                delete=False,
            ) as file:
                temporary = Path(file.name)
                json.dump(data, file, indent=2, ensure_ascii=False)
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())

            os.replace(temporary, self.path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

        return data["locations"][location_id]

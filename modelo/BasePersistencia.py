from dataclasses import field

from typing import ClassVar


class BasePersistente:
    id: str = field(init=False)
    archivo: ClassVar[str] = ""
    campo_id: ClassVar[str] = "id"

    def guardar(self):
from __future__ import annotations

from uuid import uuid4

def generar_id(prefijo: str) -> str:
    return f"{prefijo}-{uuid4().hex[:8]}"

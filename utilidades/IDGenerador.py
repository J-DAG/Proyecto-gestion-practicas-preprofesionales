from uuid import uuid4

def id_generador(prefijo: str) -> str:
    return f"{prefijo}-{uuid4().hex[:8]}"
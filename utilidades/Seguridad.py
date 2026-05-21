import hashlib


class Seguridad:
    @staticmethod
    def cifrar_clave(clave: str) -> str:
        return hashlib.sha256(clave.encode('utf-8')).hexdigest()

    @staticmethod
    def verificar_clave(clave: str,clave_hash) -> bool:
        return Seguridad.cifrar_clave(clave) == clave_hash
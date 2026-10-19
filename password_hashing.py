"""
Hash de senhas do SPECTRUM-LAB PRO (somente biblioteca padrão).

- Novas senhas: PBKDF2-HMAC-SHA256 com sal aleatório de 16 bytes e 600 000 iterações.
- Hashes antigos (SHA-256 puro, sem sal) continuam válidos para login, mas são
  marcados para regravação com o formato novo após um login bem-sucedido.
"""

import hashlib
import hmac
import secrets
from typing import Optional, Tuple

PBKDF2_ITERATIONS = 600_000
PBKDF2_PREFIX = "pbkdf2_sha256"
MIN_PASSWORD_LENGTH = 8


def hash_password(password: str) -> str:
    """Gera o hash no formato 'pbkdf2_sha256$iterações$sal$digest'."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"{PBKDF2_PREFIX}${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> Tuple[bool, bool]:
    """
    Confere a senha com o hash armazenado.
    Retorna (senha_correta, precisa_regravar).
    """
    if stored_hash.startswith(PBKDF2_PREFIX + "$"):
        try:
            _, iterations_text, salt_hex, digest_hex = stored_hash.split("$")
            iterations = int(iterations_text)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(digest_hex)
        except ValueError:
            return False, False
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(candidate, expected), False

    # Formato legado: SHA-256 sem sal. Válido apenas para migração.
    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy, stored_hash), True


def validate_new_password(password: str) -> Optional[str]:
    """Retorna a mensagem de erro para uma senha inadequada, ou None se aceitável."""
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"A senha deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres."
    if password.strip() == "":
        return "A senha não pode conter apenas espaços."
    return None

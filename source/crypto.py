import os

import argon2.low_level
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ARGON2_TIME_COST = 3
ARGON2_MEMORY_COST = 65536
ARGON2_PARALLELISM = 4

SALT_LEN = 16
NONCE_LEN = 12
TAG_LEN = 16
OVERHEAD = SALT_LEN + NONCE_LEN + TAG_LEN


def encrypt(plaintext: bytes, password: str) -> bytes:
    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)

    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    return salt + nonce + ciphertext


def decrypt(encrypted_blob: bytes, password: str) -> bytes:
    if len(encrypted_blob) < OVERHEAD:
        raise ValueError("Зашифрованные данные повреждены (слишком короткие).")

    salt = encrypted_blob[:SALT_LEN]
    nonce = encrypted_blob[SALT_LEN : SALT_LEN + NONCE_LEN]
    ciphertext = encrypted_blob[SALT_LEN + NONCE_LEN :]

    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)


def _derive_key(password: str, salt: bytes) -> bytes:
    return argon2.low_level.hash_secret_raw(
        secret=password.encode("utf-8"),
        salt=salt,
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEMORY_COST,
        parallelism=ARGON2_PARALLELISM,
        hash_len=32,
        type=argon2.low_level.Type.ID,
    )

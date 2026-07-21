from source.crypto import NONCE_LEN, OVERHEAD, SALT_LEN, decrypt, encrypt


class TestCrypto:
    def test_encrypt_decrypt_roundtrip(self):
        data = b"secret data"
        encrypted = encrypt(data, "password123")
        decrypted = decrypt(encrypted, "password123")
        assert decrypted == data

    def test_overhead_size(self):
        data = b"test"
        encrypted = encrypt(data, "pass")
        assert len(encrypted) == len(data) + OVERHEAD

    def test_structure_salt_nonce_ciphertext(self):
        encrypted = encrypt(b"x", "pass")
        salt = encrypted[:SALT_LEN]
        nonce = encrypted[SALT_LEN : SALT_LEN + NONCE_LEN]
        ct = encrypted[SALT_LEN + NONCE_LEN :]
        assert len(salt) == SALT_LEN
        assert len(nonce) == NONCE_LEN
        assert len(ct) >= 16  # ciphertext + tag

    def test_wrong_password_raises(self):
        encrypted = encrypt(b"hello", "correct")
        try:
            decrypt(encrypted, "wrong")
            assert False, "Should have raised"
        except Exception:
            pass

    def test_truncated_data_raises(self):
        try:
            decrypt(b"tooshort", "pass")
            assert False, "Should have raised"
        except ValueError:
            pass

    def test_different_ciphertexts_each_time(self):
        data = b"same data"
        e1 = encrypt(data, "pass")
        e2 = encrypt(data, "pass")
        assert e1 != e2

    def test_unicode_password(self):
        data = b"data"
        encrypted = encrypt(data, "пароль 🤫")
        decrypted = decrypt(encrypted, "пароль 🤫")
        assert decrypted == data

    def test_large_data(self):
        data = b"B" * 50000
        encrypted = encrypt(data, "pass")
        decrypted = decrypt(encrypted, "pass")
        assert decrypted == data

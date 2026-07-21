import numpy as np

from source.core import decode, encode, get_capacity


class TestImageCapacity:
    def test_capacity_positive(self, test_image):
        cap = get_capacity(test_image)
        assert cap > 0

    def test_capacity_formula(self, test_image):
        cap = get_capacity(test_image)
        assert cap == 933


class TestImageEncodeDecode:
    def test_without_password(self, test_image, short_message, tmp_path):
        out = tmp_path / "out.png"
        encode(test_image, short_message, out)
        decoded = decode(out)
        assert decoded == short_message

    def test_with_password(self, test_image, short_message, tmp_path):
        out = tmp_path / "out.png"
        encode(test_image, short_message, out, password="secret123")
        decoded = decode(out, password="secret123")
        assert decoded == short_message

    def test_wrong_password_returns_raw(self, test_image, short_message, tmp_path):
        out = tmp_path / "out.png"
        encode(test_image, short_message, out, password="pass")
        raw = decode(out, password="wrong")
        assert raw != short_message

    def test_no_password_with_encrypted(self, test_image, short_message, tmp_path):
        out = tmp_path / "out.png"
        encode(test_image, short_message, out, password="pass")
        raw = decode(out)
        assert raw != short_message

    def test_empty_data_raises(self, test_image, tmp_path):
        out = tmp_path / "out.png"
        try:
            encode(test_image, b"", out)
            assert False, "Should have raised"
        except ValueError:
            pass

    def test_too_much_data_raises(self, test_image, tmp_path):
        out = tmp_path / "out.png"
        huge = b"X" * 10000
        try:
            encode(test_image, huge, out)
            assert False, "Should have raised"
        except ValueError:
            pass

    def test_rgba_image(self, tmp_path):
        path = tmp_path / "rgba.png"
        arr = np.random.randint(0, 256, (10, 10, 4), dtype=np.uint8)
        from PIL import Image

        Image.fromarray(arr, mode="RGBA").save(path)

        msg = b"RGBA test"
        out = tmp_path / "out.png"
        encode(path, msg, out)
        decoded = decode(out)
        assert decoded == msg

    def test_grayscale_image(self, tmp_path):
        path = tmp_path / "gray.png"
        arr = np.random.randint(0, 256, (10, 10), dtype=np.uint8)
        from PIL import Image

        Image.fromarray(arr, mode="L").save(path)

        msg = b"Gray"
        out = tmp_path / "out.png"
        encode(path, msg, out)
        decoded = decode(out)
        assert decoded == msg

    def test_unicode_data(self, test_image, tmp_path):
        msg = "Привет, стеганография! 😊".encode()
        out = tmp_path / "out.png"
        encode(test_image, msg, out)
        decoded = decode(out)
        assert decoded == msg

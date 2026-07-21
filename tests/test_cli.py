import subprocess
import sys


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "source.cli", *args],
        capture_output=True,
        text=True,
    )


class TestCLIEncode:
    def test_encode_decode_image(self, test_image, short_message, tmp_path):
        out = tmp_path / "out.png"
        r = _run(
            "encode", str(test_image), "--text", short_message.decode(), "-o", str(out)
        )
        assert r.returncode == 0, f"encode failed: {r.stderr}"

        r2 = _run("decode", str(out))
        assert r2.returncode == 0, f"decode failed: {r2.stderr}"
        assert short_message.decode() in r2.stdout

    def test_encode_decode_with_password(self, test_image, short_message, tmp_path):
        out = tmp_path / "out.png"
        r = _run(
            "encode",
            str(test_image),
            "--text",
            short_message.decode(),
            "-p",
            "mypass",
            "-o",
            str(out),
        )
        assert r.returncode == 0

        r2 = _run("decode", str(out), "-p", "mypass")
        assert r2.returncode == 0
        assert short_message.decode() in r2.stdout

    def test_encode_audio(self, test_audio_wav, short_message, tmp_path):
        out = tmp_path / "out.wav"
        r = _run(
            "encode",
            str(test_audio_wav),
            "--text",
            short_message.decode(),
            "-o",
            str(out),
        )
        assert r.returncode == 0

        r2 = _run("decode", str(out))
        assert r2.returncode == 0
        assert short_message.decode() in r2.stdout

    def test_empty_text_raises(self, test_image, tmp_path):
        r = _run(
            "encode", str(test_image), "--text", "", "-o", str(tmp_path / "out.png")
        )
        assert r.returncode != 0

    def test_missing_file_shows_error(self, tmp_path):
        r = _run("encode", "/nonexistent.png", "--text", "hello")
        assert r.returncode != 0


class TestCLIDecode:
    def test_decode_save_to_file(self, test_image, short_message, tmp_path):
        encoded = tmp_path / "encoded.png"
        _run(
            "encode",
            str(test_image),
            "--text",
            short_message.decode(),
            "-o",
            str(encoded),
        )

        result = tmp_path / "result.txt"
        r = _run("decode", str(encoded), "-o", str(result))
        assert r.returncode == 0
        assert result.read_text() == short_message.decode()

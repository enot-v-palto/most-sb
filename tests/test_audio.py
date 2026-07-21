from source.core import decode, encode, get_capacity


class TestAudioWAV:
    def test_capacity(self, test_audio_wav):
        cap = get_capacity(test_audio_wav)
        assert cap == 5508

    def test_without_password(self, test_audio_wav, short_message, tmp_path):
        out = tmp_path / "out.wav"
        encode(test_audio_wav, short_message, out)
        decoded = decode(out)
        assert decoded == short_message

    def test_with_password(self, test_audio_wav, short_message, tmp_path):
        out = tmp_path / "out.wav"
        encode(test_audio_wav, short_message, out, password="pass")
        decoded = decode(out, password="pass")
        assert decoded == short_message

    def test_wrong_password_returns_raw(self, test_audio_wav, short_message, tmp_path):
        out = tmp_path / "out.wav"
        encode(test_audio_wav, short_message, out, password="pass")
        raw = decode(out, password="wrong")
        assert raw != short_message

    def test_empty_data_raises(self, test_audio_wav, tmp_path):
        out = tmp_path / "out.wav"
        try:
            encode(test_audio_wav, b"", out)
            assert False, "Should have raised"
        except ValueError:
            pass

    def test_too_much_data_raises(self, test_audio_wav, tmp_path):
        out = tmp_path / "out.wav"
        try:
            encode(test_audio_wav, b"X" * 100000, out)
            assert False, "Should have raised"
        except ValueError:
            pass


class TestAudioFLAC:
    def test_without_password(self, test_audio_flac, short_message, tmp_path):
        out = tmp_path / "out.flac"
        encode(test_audio_flac, short_message, out)
        decoded = decode(out)
        assert decoded == short_message

    def test_with_password(self, test_audio_flac, short_message, tmp_path):
        out = tmp_path / "out.flac"
        encode(test_audio_flac, short_message, out, password="pass")
        decoded = decode(out, password="pass")
        assert decoded == short_message


class TestAudioStereo:
    def test_stereo_wav(self, short_message, tmp_path):
        import numpy as np
        import soundfile as sf

        sr = 44100
        t = np.linspace(0, 0.5, int(sr * 0.5), endpoint=False)
        s = (np.sin(2 * np.pi * 440 * t) * 0.3 * 32767).astype(np.int16)
        stereo = np.column_stack((s, s))
        src = tmp_path / "stereo.wav"
        sf.write(src, stereo, sr, subtype="PCM_16")

        out = tmp_path / "out.wav"
        encode(src, short_message, out)
        decoded = decode(out)
        assert decoded == short_message

import numpy as np
import pytest
import soundfile as sf
from PIL import Image


@pytest.fixture
def test_image(tmp_path):
    path = tmp_path / "test.png"
    img = Image.fromarray(np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8))
    img.save(path)
    return path


@pytest.fixture
def test_audio_wav(tmp_path):
    path = tmp_path / "test.wav"
    sr = 44100
    t = np.linspace(0, 1, sr, endpoint=False)
    s = (np.sin(2 * np.pi * 440 * t) * 0.3 * 32767).astype(np.int16)
    sf.write(path, s, sr, subtype="PCM_16")
    return path


@pytest.fixture
def test_audio_flac(tmp_path):
    path = tmp_path / "test.flac"
    sr = 44100
    t = np.linspace(0, 1, sr, endpoint=False)
    s = (np.sin(2 * np.pi * 440 * t) * 0.3 * 32767).astype(np.int16)
    sf.write(path, s, sr, subtype="PCM_16")
    return path


@pytest.fixture
def short_message():
    return b"Hello, most-sb!"

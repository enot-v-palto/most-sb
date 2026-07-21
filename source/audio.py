import hashlib
import struct
from pathlib import Path

import numpy as np
import soundfile as sf

from .crypto import OVERHEAD, decrypt, encrypt

AUDIO_EXTENSIONS = {".wav", ".flac"}


def _password_to_seed(password: str) -> int:
    h = hashlib.sha256(password.encode()).digest()[:8]
    return int.from_bytes(h, "little")


def _get_random_positions(seed: int, count: int, start: int, end: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return start + rng.choice(end - start, size=count, replace=False)


def _read_audio(audio_path: Path) -> tuple[np.ndarray, int, int, str, int]:
    info = sf.info(audio_path)
    samples, sr = sf.read(audio_path, dtype="int16", always_2d=False)
    if samples.ndim == 1:
        samples = samples.reshape(-1, 1)
    return samples, sr, info.channels, info.subtype, samples.size


def get_capacity(audio_path: str | Path) -> int:
    audio_path = Path(audio_path)
    info = sf.info(audio_path)
    total_samples = info.frames * info.channels
    max_bytes = (total_samples // 8) - 4
    return max(0, max_bytes)


def encode(
    audio_path: str | Path,
    data: bytes,
    output_path: str | Path,
    password: str | None = None,
) -> None:
    audio_path = Path(audio_path)
    output_path = Path(output_path)

    if not data:
        raise ValueError("Нет данных для встраивания.")

    if password:
        data = encrypt(data, password)

    samples, sr, channels, subtype, total_samples = _read_audio(audio_path)
    flat = samples.ravel().astype(np.int16)

    length_bytes = struct.pack("<I", len(data))
    payload = length_bytes + data
    bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))

    if bits.size > total_samples:
        max_bytes = (total_samples // 8) - 4
        raise ValueError(
            f"Аудио-файл слишком мал для переданных данных.\n"
            f"  Максимум байт текста: {max_bytes}\n"
            f"  Передано байт текста: {len(data)}\n"
            f"  (с шифрованием накладные расходы: +{OVERHEAD} байт)"
        )

    if password:
        seed = _password_to_seed(password)
        flat[:32] = (flat[:32] & 0b11111110) | bits[:32].astype(np.int16)

        data_bits = bits[32:].astype(np.int16)
        positions = _get_random_positions(seed, len(data_bits), 32, total_samples)
        flat[positions] = (flat[positions] & 0b11111110) | data_bits
    else:
        flat[: bits.size] = (flat[: bits.size] & 0b11111110) | bits.astype(np.int16)

    result = flat.reshape(-1, channels)
    sf.write(str(output_path), result, sr, subtype=subtype)


def decode(
    audio_path: str | Path,
    password: str | None = None,
) -> bytes:
    audio_path = Path(audio_path)

    samples, _sr, _channels, _subtype, total_samples = _read_audio(audio_path)
    flat = samples.ravel()

    length_bits = flat[:32] & 1
    length_bytes = np.packbits(length_bits).tobytes()
    data_length = struct.unpack("<I", length_bytes[:4])[0]

    data_bit_count = data_length * 8
    if 32 + data_bit_count > total_samples:
        data_length = max(0, (total_samples - 32) // 8)
        data_bit_count = data_length * 8

    if password:
        seed = _password_to_seed(password)
        positions = _get_random_positions(seed, data_bit_count, 32, total_samples)
        data_bits = flat[positions] & 1
    else:
        data_bits = flat[32 : 32 + data_bit_count] & 1

    raw_data = np.packbits(data_bits).tobytes()[:data_length]

    if password:
        try:
            return decrypt(raw_data, password)
        except Exception:
            pass

    return raw_data


def is_audio_file(file_path: str | Path) -> bool:
    return Path(file_path).suffix.lower() in AUDIO_EXTENSIONS

import hashlib
import struct
from pathlib import Path

import numpy as np
from PIL import Image

from .crypto import OVERHEAD, decrypt, encrypt

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}


def _is_image(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTENSIONS


def _is_audio(path: Path) -> bool:
    from .audio import is_audio_file

    return is_audio_file(path)


def _password_to_seed(password: str) -> int:
    h = hashlib.sha256(password.encode()).digest()[:8]
    return int.from_bytes(h, "little")


def _get_random_positions(seed: int, count: int, start: int, end: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return start + rng.choice(end - start, size=count, replace=False)


def _resolve_image_mode(img: Image.Image) -> tuple[Image.Image, str, int]:
    if img.mode == "RGBA":
        return img, "RGBA", 4
    if img.mode == "RGB":
        return img, "RGB", 3
    if img.mode == "L":
        return img, "L", 1
    return img.convert("RGB"), "RGB", 3


def get_capacity(media_path: str | Path) -> int:
    media_path = Path(media_path)
    if _is_audio(media_path):
        from .audio import get_capacity as audio_get_capacity

        return audio_get_capacity(media_path)

    image_path = media_path
    img: Image.Image = Image.open(image_path)
    _, _, channels = _resolve_image_mode(img)
    w, h = img.size
    total_channels = w * h * channels
    max_bytes = (total_channels // 8) - 4
    return max(0, max_bytes)


def encode(
    media_path: str | Path,
    data: bytes,
    output_path: str | Path,
    password: str | None = None,
) -> None:
    media_path = Path(media_path)
    output_path = Path(output_path)

    if _is_audio(media_path):
        from .audio import encode as audio_encode

        return audio_encode(media_path, data, output_path, password=password)

    image_path = media_path

    if not data:
        raise ValueError("Нет данных для встраивания.")

    if password:
        data = encrypt(data, password)

    img: Image.Image = Image.open(image_path)
    img, mode, channels = _resolve_image_mode(img)
    img_array = np.array(img, dtype=np.uint8)
    h, w = img_array.shape[:2]
    total_channels = h * w * channels

    length_bytes = struct.pack("<I", len(data))
    payload = length_bytes + data

    bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))

    if bits.size > total_channels:
        max_bytes = (total_channels // 8) - 4
        raise ValueError(
            f"Изображение слишком мало для переданных данных.\n"
            f"  Максимум байт текста: {max_bytes}\n"
            f"  Передано байт текста: {len(data)}\n"
            f"  (с шифрованием накладные расходы: +{OVERHEAD} байт)"
        )

    flat = img_array.ravel()

    if password:
        seed = _password_to_seed(password)
        flat[:32] = (flat[:32] & 0b11111110) | bits[:32]

        data_bits = bits[32:]
        positions = _get_random_positions(seed, len(data_bits), 32, total_channels)
        flat[positions] = (flat[positions] & 0b11111110) | data_bits
    else:
        flat[: bits.size] = (flat[: bits.size] & 0b11111110) | bits

    if mode == "L":
        result_img = Image.fromarray(flat.reshape(h, w), mode="L")
    else:
        result_img = Image.fromarray(flat.reshape(h, w, channels), mode=mode)
    result_img.save(output_path, format="PNG", optimize=True, compress_level=9)


def decode(
    media_path: str | Path,
    password: str | None = None,
) -> bytes:
    media_path = Path(media_path)

    if _is_audio(media_path):
        from .audio import decode as audio_decode

        return audio_decode(media_path, password=password)

    image_path = media_path

    img: Image.Image = Image.open(image_path)

    if img.mode == "P":
        img = img.convert("RGB")

    img_array = np.array(img, dtype=np.uint8)
    flat = img_array.ravel()
    total_channels = flat.size

    length_bits = flat[:32] & 1
    length_bytes = np.packbits(length_bits).tobytes()
    data_length = struct.unpack("<I", length_bytes[:4])[0]

    data_bit_count = data_length * 8
    if 32 + data_bit_count > total_channels:
        data_length = max(0, (total_channels - 32) // 8)
        data_bit_count = data_length * 8

    if password:
        seed = _password_to_seed(password)
        positions = _get_random_positions(seed, data_bit_count, 32, total_channels)
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

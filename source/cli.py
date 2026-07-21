#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

from .core import decode, encode


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="most-sb",
        description=(
            "LSB стеганография — встраивание/извлечение текста в PNG и аудио (WAV/FLAC)"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    enc = sub.add_parser("encode", help="Встроить текст в файл")
    enc.add_argument(
        "media",
        type=Path,
        help="Путь к исходному файлу (PNG, WAV, FLAC, ...)",
    )
    enc.add_argument("--text", "-t", type=str, default="", help="Текст для встраивания")
    enc.add_argument("--text-file", "-f", type=Path, help="Файл с текстом")
    enc.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Результирующий файл (по умолчанию secret_<имя>)",
    )
    enc.add_argument(
        "--password",
        "-p",
        type=str,
        default=None,
        help="Пароль для шифрования (AES-256-GCM)",
    )

    dec = sub.add_parser("decode", help="Извлечь текст из файла")
    dec.add_argument(
        "media",
        type=Path,
        help="Путь к файлу со встроенным текстом (PNG, WAV, FLAC, ...)",
    )
    dec.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Сохранить извлечённый текст в файл (по умолчанию stdout)",
    )
    dec.add_argument(
        "--password",
        "-p",
        type=str,
        default=None,
        help="Пароль для расшифровки (AES-256-GCM)",
    )

    args = parser.parse_args()

    if args.command == "encode":
        if args.text and args.text_file:
            print(
                "Ошибка: укажите только --text или --text-file, не оба.",
                file=sys.stderr,
            )
            sys.exit(1)
        if args.text_file:
            text = args.text_file.read_text(encoding="utf-8")
        else:
            text = args.text
        if not text:
            print("Ошибка: текст не может быть пустым.", file=sys.stderr)
            sys.exit(1)

        data = text.encode("utf-8")
        try:
            output = args.output or Path(f"secret_{args.media.stem}{args.media.suffix}")
            encode(args.media, data, output, password=args.password)
            print(f"[OK] Данные встроены: {output.resolve()}")
        except Exception as e:
            print(f"[ERR] Ошибка: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "decode":
        raw_data = decode(args.media, password=args.password)
        try:
            text = raw_data.decode("utf-8")
        except UnicodeDecodeError:
            text = raw_data.hex()

        if args.output:
            args.output.write_text(text, encoding="utf-8")
            print(f"[OK] Текст сохранён: {args.output.resolve()}")
        else:
            print(text)


if __name__ == "__main__":
    main()

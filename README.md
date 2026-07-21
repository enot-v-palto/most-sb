# most-sb — LSB стеганография

Прячет текст внутри PNG-изображений и WAV/FLAC-аудиофайлов, меняя последние биты пикселей или сэмплов.  
Опциональное шифрование AES-256-GCM + Argon2id.

## Установка

```bash
pip install git+https://github.com/enot-v-palto/most-sb
```

Готовые бинарники (Linux/macOS/Windows) — на странице [releases](https://github.com/enot-v-palto/most-sb/releases).

## Использование

### CLI

```bash
most-sb encode image.png --text "секретное сообщение" -o output.png
most-sb encode audio.wav --text "секрет" -p mypassword
most-sb decode output.png
most-sb decode output.png -p mypassword -o result.txt
```

### TUI

```bash
most-sb-tui
```

Две закладки: Шифрование и Расшифровка.

## Как это работает

LSB (Least Significant Bit) — младший бит каждого пикселя (R/G/B/A) или сэмпла заменяется битом сообщения.  
Человеческий глаз/ухо разницы не замечает.

- **Без пароля** — данные пишутся последовательно: `[4 байта длина][сообщение]`
- **С паролем** — данные шифруются AES-256-GCM с ключом от Argon2id и распределяются по псевдослучайным позициям
- **Deniable decryption** — неверный пароль возвращает сырые байты, ничего не падает

## Ёмкость

```
изображение: макс_байт = (ширина × высота × каналы // 8) - 4
аудио:      макс_байт = (сэмплы × каналы // 8) - 4
```

1000×1000 RGB ≈ 375 КБ текста.  
1 мин 44100 Гц стерео ≈ 661 КБ.

## Форматы

- **Изображения:** PNG (вход и выход)
- **Аудио:** WAV, FLAC (lossless)
- **Другие форматы** (JPEG, BMP, WEBP) конвертируются в PNG
- MP3/AAC не поддерживаются — потери качества разрушают LSB

## Требования

- Python ≥ 3.11
- pillow, numpy, textual, cryptography, soundfile, argon2-cffi

## Релиз

```bash
git tag v0.1.0 && git push --tags
```

GitHub Actions соберёт бинарники под Ubuntu, macOS, Windows и создаст Release.

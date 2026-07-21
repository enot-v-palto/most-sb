import locale
import os

_LANG = os.environ.get("MOST_SB_LANG")
if not _LANG:
    try:
        loc = locale.getlocale()[0]
        _LANG = loc[:2] if loc else None
    except Exception:
        pass
if _LANG not in ("en", "ru"):
    _LANG = "ru"

STR = {
    "ru": {
        "app_title": "Most-SB — LSB стеганография (с открытым исходным кодом)",
        "browse_title": "Выберите файл",
        "cancel": "Отмена",
        "tab_encode": "Шифрование",
        "tab_decode": "Расшифровка",
        "file_label": "Файл:",
        "file_placeholder": "поддерживаются: PNG, WAV, FLAC",
        "browse": "Обзор",
        "password_label": "Пароль (опционально):",
        "password_placeholder": "пароль",
        "msg_label_encode": "Скрываемое сообщение:",
        "msg_label_decode": "Извлечённое сообщение:",
        "btn_encode": "Зашифровать",
        "btn_decode": "Расшифровать",
        "btn_clear": "Очистить",
        "decode_hint": (
            "Если результат нечитаем — вероятно, "
            "неправильный пароль или данные повреждены"
        ),
        "err_no_file": "Укажите файл.",
        "err_no_text": "Введите текст для встраивания.",
        "file_not_found": "Файл не найден: {path}",
        "waiting": "⏳ Пожалуйста, подождите...",
        "done_encoded": "Готово! Сохранено: {path}\nВстроено байт: {n}",
        "encrypted_note": "Данные зашифрованы паролем.",
        "error": "Ошибка: {e}",
        "done_decoded": "Готово! Извлечено байт: {n}",
        "max_capacity": "Максимум: {n} байт",
        "used_capacity": "Занято: {used} из {total} байт",
        "mono": "моно",
        "stereo": "стерео",
        "fmt_warning": (
            "⚠️ Формат {fmt} будет сконвертирован в PNG (размер может вырасти)."
        ),
        "history_title": "История операций:",
        "history_time": "Время",
        "history_op": "Операция",
        "history_file": "Файл",
        "history_status": "Статус",
        "op_encode": "шифрование",
        "op_decode": "расшифровка",
        "op_ok": "OK",
        "op_err": "ERR",
        "kb_clear": "Очистить",
        "kb_clear_history": "Очистить историю",
    },
    "en": {
        "app_title": "Most-SB — LSB steganography (open source)",
        "browse_title": "Select file",
        "cancel": "Cancel",
        "tab_encode": "Encode",
        "tab_decode": "Decode",
        "file_label": "File:",
        "file_placeholder": "supported: PNG, WAV, FLAC",
        "browse": "Browse",
        "password_label": "Password (optional):",
        "password_placeholder": "password",
        "msg_label_encode": "Message to hide:",
        "msg_label_decode": "Extracted message:",
        "btn_encode": "Encode",
        "btn_decode": "Decode",
        "btn_clear": "Clear",
        "decode_hint": (
            "If the result is garbled — likely wrong password or corrupted data"
        ),
        "err_no_file": "Specify a file.",
        "err_no_text": "Enter text to hide.",
        "file_not_found": "File not found: {path}",
        "waiting": "⏳ Please wait...",
        "done_encoded": "Done! Saved: {path}\nBytes embedded: {n}",
        "encrypted_note": "Data is encrypted with a password.",
        "error": "Error: {e}",
        "done_decoded": "Done! Extracted bytes: {n}",
        "max_capacity": "Max: {n} bytes",
        "used_capacity": "Used: {used} of {total} bytes",
        "mono": "mono",
        "stereo": "stereo",
        "fmt_warning": (
            "⚠️ Format {fmt} will be converted to PNG (file size may increase)."
        ),
        "history_title": "Operation history:",
        "history_time": "Time",
        "history_op": "Operation",
        "history_file": "File",
        "history_status": "Status",
        "op_encode": "encode",
        "op_decode": "decode",
        "op_ok": "OK",
        "op_err": "ERR",
        "kb_clear": "Clear",
        "kb_clear_history": "Clear history",
    },
}


def _(key: str) -> str:
    return STR.get(_LANG, STR["ru"]).get(key, key)  # type: ignore[arg-type]

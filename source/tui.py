#!/usr/bin/env python3

from datetime import datetime
from pathlib import Path

from PIL import Image as PILImage
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    DirectoryTree,
    Footer,
    Header,
    Input,
    Label,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
)

from .core import decode, encode, get_capacity
from .strings import _

HISTORY_MAX = 50


class FileBrowser(ModalScreen):
    TITLE = _("browse_title")

    BINDINGS = [("escape", "cancel")]

    def compose(self) -> ComposeResult:
        yield DirectoryTree(Path.home().resolve().as_posix(), id="file-tree")
        yield Button(_("cancel"), id="fb-cancel", variant="default")

    @on(DirectoryTree.FileSelected)
    def file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.dismiss(event.path)

    @on(Button.Pressed, "#fb-cancel")
    def on_cancel(self) -> None:
        self.dismiss()

    def action_cancel(self) -> None:
        self.dismiss()


class StegoApp(App):
    TITLE = _("app_title")

    CSS = """
    TabbedContent {
        margin: 1 2 0 2;
    }
    TabPane {
        padding: 1 2;
    }
    Label {
        text-style: bold;
    }
    .file-row {
        height: 3;
        align: center middle;
        margin-bottom: 0;
    }
    .file-row > Input {
        margin-bottom: 0;
        width: 1fr;
    }
    .file-row > Button {
        width: 10;
        margin-left: 1;
        margin-right: 0;
    }
    .pwd-row {
        height: 3;
        align: center middle;
        margin-bottom: 0;
    }
    .pwd-row > Input {
        margin-bottom: 0;
        width: 1fr;
    }
    .pwd-row > Button {
        width: 4;
        margin-right: 0;
        margin-left: 1;
    }
    TextArea {
        height: 12;
        border: solid cyan;
        margin-bottom: 0;
    }
    Horizontal {
        align: left middle;
        margin-bottom: 0;
    }
    Button {
        margin-right: 1;
    }
    .label-over {
        color: red;
    }
    .meta-info {
        color: $text-muted;
        text-style: italic;
        margin-bottom: 0;
    }
    .bottom-row {
        height: auto;
        max-height: 4;
    }
    .action-col {
        width: 1fr;
    }
    .action-col > Horizontal {
        margin-bottom: 0;
    }
    .top-section {
        height: auto;
        min-height: 9;
        margin-bottom: 1;
    }
    .top-left, .top-right {
        width: 1fr;
        height: auto;
    }
    .top-right {
        margin-left: 1;
        border-left: solid $border;
        padding-left: 1;
    }
    .top-right > DataTable {
        height: 8;
    }
    .waiting {
        color: $warning;
        text-style: bold;
    }
    #dec-hint {
        color: $text-muted;
        text-style: italic;
        margin-top: 1;
        display: none;
    }
    """

    BINDINGS = [
        ("escape", "clear_active", _("kb_clear")),
        ("ctrl+l", "clear_history", _("kb_clear_history")),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._history: list[dict] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="tab-encode"):
            with TabPane(_("tab_encode"), id="tab-encode"):
                with ScrollableContainer():
                    with Horizontal(classes="top-section"):
                        with Vertical(classes="top-left"):
                            yield Label(_("file_label"), id="enc-image-label")
                            with Horizontal(classes="file-row"):
                                yield Input(
                                    placeholder=_("file_placeholder"),
                                    id="enc-image",
                                )
                                yield Button(
                                    _("browse"), id="enc-browse", variant="default"
                                )
                            yield Static(id="enc-meta", classes="meta-info")
                            yield Label(_("password_label"))
                            with Horizontal(classes="pwd-row"):
                                yield Input(
                                    id="enc-password",
                                    password=True,
                                )
                                yield Button(
                                    "👁", id="enc-pwd-toggle", variant="default"
                                )
                        with Vertical(classes="top-right"):
                            yield Label(_("history_title"))
                            yield DataTable(id="enc-history-table")
                    yield Label(_("msg_label_encode"), id="enc-text-label")
                    yield TextArea(id="enc-text", show_line_numbers=True)
                    with Horizontal(classes="bottom-row"):
                        with Vertical(classes="action-col"):
                            with Horizontal():
                                yield Button(
                                    _("btn_encode"), id="btn-encode", variant="primary"
                                )
                                yield Button(
                                    _("btn_clear"),
                                    id="btn-enc-clear",
                                    variant="default",
                                )
                            yield Static(id="enc-status")

            with TabPane(_("tab_decode"), id="tab-decode"):
                with ScrollableContainer():
                    with Horizontal(classes="top-section"):
                        with Vertical(classes="top-left"):
                            yield Label(_("file_label"))
                            with Horizontal(classes="file-row"):
                                yield Input(
                                    placeholder=_("file_placeholder"),
                                    id="dec-image",
                                )
                                yield Button(
                                    _("browse"), id="dec-browse", variant="default"
                                )
                            yield Static(id="dec-meta", classes="meta-info")
                            yield Label(_("password_label"))
                            with Horizontal(classes="pwd-row"):
                                yield Input(
                                    id="dec-password",
                                    password=True,
                                )
                                yield Button(
                                    "👁", id="dec-pwd-toggle", variant="default"
                                )
                        with Vertical(classes="top-right"):
                            yield Label(_("history_title"))
                            yield DataTable(id="dec-history-table")
                    yield Label(_("msg_label_decode"))
                    yield TextArea(
                        id="dec-text", read_only=True, show_line_numbers=True
                    )
                    with Horizontal(classes="bottom-row"):
                        with Vertical(classes="action-col"):
                            with Horizontal():
                                yield Button(
                                    _("btn_decode"), id="btn-decode", variant="primary"
                                )
                                yield Button(
                                    _("btn_clear"),
                                    id="btn-dec-clear",
                                    variant="default",
                                )
                            yield Static(id="dec-status")
                            yield Label(_("decode_hint"), id="dec-hint")
        yield Footer()

    def on_mount(self) -> None:
        for table_id in ("enc-history-table", "dec-history-table"):
            table = self.query_one(f"#{table_id}", DataTable)
            table.add_columns(
                _("history_time"),
                _("history_op"),
                _("history_file"),
                _("history_status"),
            )

    @on(Button.Pressed, "#enc-browse")
    def on_enc_browse(self) -> None:
        self.push_screen(FileBrowser(), self._enc_browse_cb)

    def _enc_browse_cb(self, path: Path | None) -> None:
        if path:
            self.query_one("#enc-image", Input).value = str(path)

    @on(Button.Pressed, "#dec-browse")
    def on_dec_browse(self) -> None:
        self.push_screen(FileBrowser(), self._dec_browse_cb)

    def _dec_browse_cb(self, path: Path | None) -> None:
        if path:
            self.query_one("#dec-image", Input).value = str(path)

    def _file_metadata(self, path_str: str) -> str:
        path = Path(path_str)
        if not path.exists():
            return ""
        size = path.stat().st_size
        size_str = _format_size(size)
        suffix = path.suffix.lower()
        try:
            if suffix in {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}:
                with PILImage.open(path) as img:
                    w, h = img.size
                    return f"{size_str} | {w}×{h} {img.mode} ({img.format})"
            elif suffix in {".wav", ".flac"}:
                import soundfile as sf

                info = sf.info(path)
                ch = _("mono") if info.channels == 1 else _("stereo")
                return (
                    f"{size_str} | {int(info.samplerate // 1000)}кГц "
                    f"{ch} | {info.duration:.1f}с"
                )
        except Exception:
            pass
        return size_str

    def _update_dec_meta(self) -> None:
        path = self.query_one("#dec-image", Input).value.strip()
        meta = self._file_metadata(path) if path and Path(path).exists() else ""
        self.query_one("#dec-meta", Static).update(meta)

    def _update_enc_indicators(self) -> None:
        image_path = self.query_one("#enc-image", Input).value.strip()
        img_label = self.query_one("#enc-image-label", Label)
        txt_label = self.query_one("#enc-text-label", Label)
        text_el = self.query_one("#enc-text", TextArea)
        meta = self.query_one("#enc-meta", Static)

        if not image_path or not Path(image_path).exists():
            meta.update("")
            img_label.update(_("file_label"))
            txt_label.update(_("msg_label_encode"))
            txt_label.remove_class("label-over")
            return

        path = Path(image_path)
        fmt_note = ""
        try:
            image_ext = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
            if path.suffix.lower() in image_ext:
                with PILImage.open(image_path) as pil_img:
                    actual_fmt = pil_img.format or ""
                if actual_fmt.upper() not in ("PNG", ""):
                    fmt_note = _("fmt_warning").format(fmt=actual_fmt)
        except Exception:
            pass

        meta_text = self._file_metadata(image_path)
        if fmt_note:
            meta_text = meta_text + " | " + fmt_note if meta_text else fmt_note
        meta.update(meta_text)

        try:
            capacity = get_capacity(image_path)
            cap_str = _("max_capacity").format(n=f"{capacity:,}".replace(",", " "))
            img_label.update(cap_str)
        except Exception:
            img_label.update(_("file_label"))
            txt_label.update(_("msg_label_encode"))
            txt_label.remove_class("label-over")
            return

        text = text_el.text
        used = len(text.encode("utf-8")) if text else 0
        used_str = _("used_capacity").format(
            used=f"{used:,}".replace(",", " "),
            total=f"{capacity:,}".replace(",", " "),
        )
        txt_label.update(used_str)

        txt_label.remove_class("label-over")
        if used > capacity:
            txt_label.add_class("label-over")

    @on(Input.Changed, "#enc-image")
    def on_enc_image_changed(self) -> None:
        self._update_enc_indicators()

    @on(Input.Changed, "#dec-image")
    def on_dec_image_changed(self) -> None:
        self._update_dec_meta()

    @on(TextArea.Changed, "#enc-text")
    def on_enc_text_changed(self) -> None:
        self._update_enc_indicators()

    @on(Button.Pressed, "#enc-pwd-toggle")
    def on_enc_pwd_toggle(self) -> None:
        pwd_input = self.query_one("#enc-password", Input)
        pwd_input.password = not pwd_input.password

    @on(Button.Pressed, "#btn-encode")
    def on_encode(self) -> None:
        image_path = self.query_one("#enc-image", Input).value.strip()
        text = self.query_one("#enc-text", TextArea).text
        password = self.query_one("#enc-password", Input).value.strip() or None
        status = self.query_one("#enc-status", Static)

        if not image_path:
            status.update(_("err_no_file"))
            return
        if not text:
            status.update(_("err_no_text"))
            return

        img = Path(image_path)
        if not img.exists():
            status.update(_("file_not_found").format(path=image_path))
            return

        output = img.parent / f"secret_{img.stem}{img.suffix}"
        status.update(_("waiting"))
        status.add_class("waiting")

        try:
            data = text.encode("utf-8")
            encode(img, data, output, password=password)
            msg = _("done_encoded").format(path=str(output.resolve()), n=len(data))
            if password:
                msg += "\n" + _("encrypted_note")
            status.remove_class("waiting")
            status.update(msg)
            self._add_history("encode", str(img), _("op_ok"))
        except Exception as e:
            status.remove_class("waiting")
            status.update(_("error").format(e=e))
            self._add_history("encode", str(img), f"{_('op_err')}: {e}")

    @on(Button.Pressed, "#btn-enc-clear")
    def on_enc_clear(self) -> None:
        self.query_one("#enc-image", Input).value = ""
        self.query_one("#enc-password", Input).value = ""
        self.query_one("#enc-text", TextArea).text = ""
        self.query_one("#enc-status", Static).update("")
        self._update_enc_indicators()

    @on(Button.Pressed, "#dec-pwd-toggle")
    def on_dec_pwd_toggle(self) -> None:
        pwd_input = self.query_one("#dec-password", Input)
        pwd_input.password = not pwd_input.password

    @on(Button.Pressed, "#btn-decode")
    def on_decode(self) -> None:
        image_path = self.query_one("#dec-image", Input).value.strip()
        password = self.query_one("#dec-password", Input).value.strip() or None
        status = self.query_one("#dec-status", Static)
        output_area = self.query_one("#dec-text", TextArea)

        if not image_path:
            status.update(_("err_no_file"))
            return

        img = Path(image_path)
        if not img.exists():
            status.update(_("file_not_found").format(path=image_path))
            return

        status.update(_("waiting"))
        status.add_class("waiting")

        data = decode(img, password=password)
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.hex()
        output_area.text = text
        status.remove_class("waiting")
        status.update(_("done_decoded").format(n=len(data)))
        self._add_history("decode", str(img), _("op_ok"))
        self.query_one("#dec-hint", Label).display = True

    @on(Button.Pressed, "#btn-dec-clear")
    def on_dec_clear(self) -> None:
        self.query_one("#dec-image", Input).value = ""
        self.query_one("#dec-password", Input).value = ""
        self.query_one("#dec-text", TextArea).text = ""
        self.query_one("#dec-status", Static).update("")
        self.query_one("#dec-meta", Static).update("")
        self.query_one("#dec-hint", Label).display = False

    def _add_history(self, operation: str, file_path: str, status: str) -> None:
        now = datetime.now().strftime("%H:%M:%S")
        self._history.insert(
            0,
            {
                "time": now,
                "op": operation,
                "file": file_path,
                "status": status,
            },
        )
        if len(self._history) > HISTORY_MAX:
            self._history.pop()
        self._refresh_history()

    def _refresh_history(self) -> None:
        for table_id in ("enc-history-table", "dec-history-table"):
            table = self.query_one(f"#{table_id}", DataTable)
            table.clear()
            for entry in self._history:
                table.add_row(
                    entry["time"],
                    entry["op"],
                    entry["file"],
                    entry["status"],
                )

    def action_clear_history(self) -> None:
        self._history.clear()
        self._refresh_history()

    def action_clear_active(self) -> None:
        focused = self.focused
        if isinstance(focused, Input):
            focused.value = ""
        elif isinstance(focused, TextArea) and not focused.read_only:
            focused.text = ""


def _format_size(size: int) -> str:
    if size < 1024:
        return f"{size} Б"
    elif size < 1024**2:
        return f"{size / 1024:.1f} КБ"
    elif size < 1024**3:
        return f"{size / 1024**2:.1f} МБ"
    return f"{size / 1024**3:.2f} ГБ"


def main() -> None:
    app = StegoApp()
    app.run()


if __name__ == "__main__":
    main()

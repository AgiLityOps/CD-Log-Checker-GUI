"""Tkinter front end for hbcl."""

from __future__ import annotations

import os
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk

from . import APP_NAME, __version__
from .core import Report, check_log, hbcl_version, to_html
from .render import BACKGROUND, FOREGROUND, COLORS, Style

PANEL = "#252526"
BUTTON = "#3a3d41"
BUTTON_ACTIVE = "#4b4f55"
STATUS_BG = "#800080"
SCROLL_TROUGH = "#1e1e1e"
SCROLL_THUMB = "#3c3c3c"
SCROLL_THUMB_HOVER = "#505050"
SCROLL_THUMB_PRESSED = "#5a5a5a"
FONT_SIZE = 12
HINT = (
    "Drag and drop one or more .log files anywhere on this window,\n"
    "or click \"Open log...\".\n\n"
    "Supports EAC (incl. 0.95 and foreign languages) and XLD logs."
)

try:  # Drag and drop support (tkdnd). Fall back to plain Tk if unavailable.
    from tkinterdnd2 import DND_FILES, TkinterDnD

    _DND_IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover
    TkinterDnD = None
    DND_FILES = None
    _DND_IMPORT_ERROR = exc


def make_root() -> tuple[tk.Tk, bool, str]:
    """Create the root window, with drag and drop if possible."""
    if TkinterDnD is not None:
        try:
            return TkinterDnD.Tk(), True, ""
        except Exception as exc:  # tkdnd binary missing / failed to load
            err = f"{exc.__class__.__name__}: {exc}"
            return tk.Tk(), False, err
    return tk.Tk(), False, str(_DND_IMPORT_ERROR)


def pick_mono_font(root: tk.Misc) -> str:
    families = {f.lower(): f for f in tkfont.families(root)}
    for name in ("Consolas", "Cascadia Mono", "DejaVu Sans Mono", "Liberation Mono",
                 "Menlo", "Courier New"):
        if name.lower() in families:
            return families[name.lower()]
    return "TkFixedFont"


class HbclApp:
    def __init__(self, root: tk.Tk, dnd_ok: bool, dnd_error: str = "") -> None:
        self.root = root
        self.dnd_ok = dnd_ok
        self.reports: list[Report] = []
        self.paths: list[str] = []
        self.translate = tk.BooleanVar(value=False)
        self.integrity = tk.BooleanVar(value=False)

        root.title(APP_NAME)
        root.configure(bg=BACKGROUND)
        root.geometry("1000x760")
        root.minsize(560, 360)
        root.report_callback_exception = self._on_tk_error
        self._set_icon()

        self.mono = pick_mono_font(root)
        self.font = tkfont.Font(root, family=self.mono, size=FONT_SIZE)
        self.font_bold = tkfont.Font(root, family=self.mono, size=FONT_SIZE,
                                     weight="bold")

        self._build_toolbar()
        self._build_text()
        self._build_status()
        self._show_hint()

        if dnd_ok:
            for widget in (root, self.text):
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind("<<Drop>>", self._on_drop)
        else:
            self.set_status(f"Drag and drop unavailable ({dnd_error}); use Open log...")

        root.bind("<Control-o>", lambda e: self.open_dialog())
        root.bind("<Control-s>", lambda e: self.save_as())
        root.bind("<Control-Shift-C>", lambda e: self.copy_all())

    def _set_icon(self):
        base = getattr(sys, "_MEIPASS", None) or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "..")
        ico = os.path.join(base, "assets", "app.ico")
        try:
            if sys.platform == "win32" and os.path.isfile(ico):
                self.root.iconbitmap(default=ico)
        except Exception:
            pass

    # ----------------------------------------------------------------- layout
    def _button(self, parent, text, command):
        return tk.Button(
            parent, text=text, command=command, bg=BUTTON, fg=FOREGROUND,
            activebackground=BUTTON_ACTIVE, activeforeground="#ffffff",
            relief="flat", bd=0, padx=12, pady=4, highlightthickness=0,
            font=(self.mono, 10), cursor="hand2",
        )

    def _check(self, parent, text, var):
        return tk.Checkbutton(
            parent, text=text, variable=var, command=self.recheck,
            bg=PANEL, fg=FOREGROUND, selectcolor=BUTTON, activebackground=PANEL,
            activeforeground="#ffffff", highlightthickness=0, bd=0,
            font=(self.mono, 10),
        )

    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg=PANEL, padx=8, pady=6)
        bar.pack(side="top", fill="x")
        self._button(bar, "Open log...", self.open_dialog).pack(side="left", padx=(0, 6))
        self._button(bar, "Copy", self.copy_all).pack(side="left", padx=(0, 6))
        self._button(bar, "Save as...", self.save_as).pack(side="left", padx=(0, 6))
        self._button(bar, "Clear", self.clear).pack(side="left", padx=(0, 16))
        self._check(bar, "Translate (foreign log to English)", self.translate).pack(
            side="left", padx=(0, 12))
        self._check(bar, "Experimental integrity check", self.integrity).pack(side="left")

    def _setup_ttk_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.layout("Dark.Vertical.TScrollbar", [
            ("Vertical.Scrollbar.trough", {"sticky": "ns", "children": [
                ("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"}),
            ]}),
        ])
        style.configure(
            "Dark.Vertical.TScrollbar", troughcolor=SCROLL_TROUGH,
            background=SCROLL_THUMB, bordercolor=SCROLL_TROUGH,
            lightcolor=SCROLL_THUMB, darkcolor=SCROLL_THUMB, arrowcolor=SCROLL_THUMB,
            gripcount=0, relief="flat", borderwidth=0, width=14, arrowsize=14,
        )
        style.map(
            "Dark.Vertical.TScrollbar",
            background=[("pressed", SCROLL_THUMB_PRESSED), ("active", SCROLL_THUMB_HOVER)],
            lightcolor=[("pressed", SCROLL_THUMB_PRESSED), ("active", SCROLL_THUMB_HOVER)],
            darkcolor=[("pressed", SCROLL_THUMB_PRESSED), ("active", SCROLL_THUMB_HOVER)],
        )

    def _build_text(self):
        self._setup_ttk_style()
        frame = tk.Frame(self.root, bg=BACKGROUND)
        frame.pack(side="top", fill="both", expand=True)
        self.text = tk.Text(
            frame, bg=BACKGROUND, fg=FOREGROUND, insertbackground=FOREGROUND,
            selectbackground="#264f78", selectforeground="#ffffff",
            font=self.font, wrap="word", relief="flat", bd=0, padx=10, pady=8,
            highlightthickness=0, undo=False,
        )
        # Dark scrollbar: native Windows scrollbars can't be recoloured, so use a
        # ttk scrollbar drawn by the platform-independent "clam" theme, with
        # the arrow buttons removed from its layout.
        vs = ttk.Scrollbar(frame, orient="vertical", command=self.text.yview,
                           style="Dark.Vertical.TScrollbar")
        self.text.configure(yscrollcommand=vs.set)
        vs.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)
        # Read-only but selectable/copyable.
        self.text.bind("<Key>", self._readonly_key)
        self.text.tag_configure("hint", foreground="#8a8a8a", justify="center")
        self.text.tag_configure("sep", foreground="#555555")
        self._tags: set[str] = set()

    def _build_status(self):
        self.status = tk.Label(
            self.root, anchor="w", bg=STATUS_BG, fg="#ffffff", padx=8, pady=2,
            font=(self.mono, 9),
        )
        self.status.pack(side="bottom", fill="x")
        self.base_status = (
            f"{APP_NAME} v{__version__} - using doujincafe/hbcl v{hbcl_version()}"
        )
        self.set_status("")

    # ----------------------------------------------------------------- helpers
    def _readonly_key(self, event):
        ctrl = event.state & 0x4
        if ctrl and event.keysym.lower() in ("c", "a"):
            if event.keysym.lower() == "a":
                self.text.tag_add("sel", "1.0", "end")
                return "break"
            return None
        if event.keysym in ("Up", "Down", "Left", "Right", "Prior", "Next", "Home", "End"):
            return None
        return "break"

    def set_status(self, msg: str):
        self.status.configure(text=self.base_status + (f"   |   {msg}" if msg else ""))

    def _tag_for(self, style: Style) -> str | None:
        if style.color is None and not style.bold:
            return None
        tag = style.tag
        if tag not in self._tags:
            self.text.tag_configure(
                tag, foreground=style.color or FOREGROUND,
                font=self.font_bold if style.bold else self.font,
            )
            self._tags.add(tag)
        return tag

    def _show_hint(self):
        self.text.delete("1.0", "end")
        self.text.insert("end", "\n\n\n" + HINT, ("hint",))

    def render(self):
        self.text.delete("1.0", "end")
        if not self.reports:
            self._show_hint()
            return
        for i, rep in enumerate(self.reports):
            if i:
                self.text.insert("end", "\n" + "\u2500" * 60 + "\n\n", ("sep",))
            for chunk, style in rep.segments:
                tag = self._tag_for(style)
                self.text.insert("end", chunk, (tag,) if tag else ())
        self.text.see("1.0")

    # ----------------------------------------------------------------- actions
    def load(self, paths):
        paths = [p for p in paths if p]
        if not paths:
            return
        self.paths = list(paths)
        self.recheck()

    def recheck(self):
        if not self.paths:
            return
        self.root.config(cursor="watch")
        self.root.update_idletasks()
        try:
            self.reports = [
                check_log(p, self.translate.get(), self.integrity.get())
                for p in self.paths
            ]
        finally:
            self.root.config(cursor="")
        self.render()
        bad = sum(1 for r in self.reports if not r.ok)
        mode = "translated" if self.translate.get() else "checked"
        msg = f"{len(self.reports)} log(s) {mode}"
        if len(self.reports) == 1 and self.reports[0].score is not None:
            msg += f", score {self.reports[0].score}"
        if bad:
            msg += f", {bad} with problems"
        self.set_status(msg)

    def _on_drop(self, event):
        try:
            paths = list(self.root.tk.splitlist(event.data))
        except Exception:
            paths = [event.data]
        self.load(paths)
        return event.action

    def open_dialog(self):
        paths = filedialog.askopenfilenames(
            parent=self.root, title="Open rip log(s)",
            filetypes=[("Rip logs", "*.log *.txt"), ("All files", "*.*")],
        )
        if paths:
            self.load(list(paths))

    def all_text(self) -> str:
        sep = "\n" + "-" * 80 + "\n\n"
        return sep.join(r.text for r in self.reports)

    def copy_all(self):
        if not self.reports:
            self.set_status("Nothing to copy yet")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.all_text())
        self.set_status("Copied report to clipboard")

    def save_as(self):
        if not self.reports:
            self.set_status("Nothing to save yet")
            return
        base = os.path.splitext(os.path.basename(self.reports[0].path))[0] or "report"
        path = filedialog.asksaveasfilename(
            parent=self.root, title="Save report",
            initialfile=f"{base}-hbcl.txt", defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("HTML (colored)", "*.html")],
        )
        if not path:
            return
        try:
            if path.lower().endswith((".html", ".htm")):
                data = to_html(self.reports)
            else:
                data = self.all_text()
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(data)
            self.set_status(f"Saved {path}")
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Could not save file:\n{exc}", parent=self.root)

    def clear(self):
        self.reports, self.paths = [], []
        self._show_hint()
        self.set_status("")

    def _on_tk_error(self, exc, val, tb):
        import traceback

        detail = "".join(traceback.format_exception(exc, val, tb))
        try:
            self.set_status(f"Unexpected error: {val}")
            self.text.insert("end", "\n\nUnexpected error:\n" + detail,
                             (self._tag_for(Style(COLORS["bad"], False)),))
        except Exception:
            pass


def selftest(log_paths: list[str], out_path: str, translate: bool = False,
             integrity: bool = False) -> int:
    """Hidden smoke test: check log(s) inside a real (hidden) Tk window and write
    the results to ``out_path``. Exit code 0 = OK, 1 = DnD missing or a single
    log failed, 2 = unexpected exception."""
    lines = []
    code = 0
    try:
        root, dnd_ok, dnd_err = make_root()
        root.withdraw()
        app = HbclApp(root, dnd_ok, dnd_err)
        app.translate.set(translate)
        app.integrity.set(integrity)
        app.load(log_paths)
        root.update()
        lines += [
            f"app={APP_NAME} {__version__}",
            f"python={sys.version.split()[0]}",
            f"hbcl={hbcl_version()}",
            f"tk={tk.TkVersion}",
            f"dnd_ok={dnd_ok} {dnd_err}".rstrip(),
            f"font={app.mono} {app.font.cget('size')}pt wrap={app.text.cget('wrap')} theme={ttk.Style(root).theme_use()}",
            f"frozen={getattr(sys, 'frozen', False)}",
            f"translate={translate} integrity={integrity}",
            f"status={app.status.cget('text')}",
            f"text_tags={len(app._tags)}",
        ]
        for rep in app.reports:
            lines += [
                "=" * 60,
                f"log={rep.path}",
                f"ok={rep.ok}",
                f"score={rep.score}",
                f"segments={len(rep.segments)}",
                "----- report head -----",
                "\n".join(rep.text.splitlines()[:16]),
            ]
        if not dnd_ok or (len(app.reports) == 1 and not app.reports[0].ok):
            code = 1
        root.destroy()
    except Exception:
        import traceback

        lines.append("EXCEPTION:\n" + traceback.format_exc())
        code = 2
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return code


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--selftest"]:
        # --selftest LOG [LOG ...] OUT [--translate] [--integrity]
        flags = {a for a in argv[1:] if a.startswith("--")}
        rest = [a for a in argv[1:] if not a.startswith("--")]
        if len(rest) < 2:
            return 3
        return selftest(rest[:-1], rest[-1], "--translate" in flags,
                        "--integrity" in flags)
    if argv[:1] in (["--version"], ["-V"]):
        print(f"{APP_NAME} {__version__} (hbcl {hbcl_version()})")
        return 0
    root, dnd_ok, dnd_err = make_root()
    app = HbclApp(root, dnd_ok, dnd_err)
    files = [a for a in argv if not a.startswith("-")]
    if files:  # e.g. a log dropped onto the exe icon / "Open with"
        root.after(50, lambda: app.load(files))
    root.mainloop()
    return 0

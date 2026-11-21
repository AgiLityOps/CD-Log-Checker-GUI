"""GUI-independent wrapper around the hbcl library."""

from __future__ import annotations

import html
import traceback
from dataclasses import dataclass, field
from importlib import metadata
from pathlib import Path

from .render import COLORS, Style


def hbcl_version() -> str:
    try:
        return metadata.version("heybrochecklog")
    except Exception:
        return "unknown"


@dataclass
class Report:
    """A rendered result: a list of (text, Style) segments."""

    path: str
    segments: list[tuple[str, Style]] = field(default_factory=list)
    score: int | None = None
    ok: bool = True

    def add(self, text: str, style: Style | None = None) -> None:
        self.segments.append((text, style or Style()))

    def add_markup(self, markup: str) -> None:
        from .render import parse_markup

        self.segments.extend(parse_markup(markup))

    @property
    def text(self) -> str:
        return "".join(t for t, _ in self.segments)


HEADER = Style(COLORS["log4"], True)
LABEL = Style("#ffffff", True)
GOOD = Style(COLORS["good"], True)
WARN = Style(COLORS["badish"], True)
BAD = Style(COLORS["bad"], True)


def _score_style(score) -> Style:
    try:
        s = int(score)
    except (TypeError, ValueError):
        return LABEL
    if s >= 100:
        return GOOD
    if s >= 80:
        return WARN
    return BAD


def check_log(path: str | Path, translate: bool = False, integrity: bool = False) -> Report:
    """Score (or translate) one log file. Never raises."""
    path = Path(path)
    report = Report(str(path))
    report.add("Log: ", LABEL)
    report.add(f"{path}\n\n", HEADER)
    try:
        if not path.is_file():
            report.ok = False
            report.add("File does not exist or is not a regular file.\n", BAD)
            return report
        if translate:
            _translate(path, report)
        else:
            _score(path, report, integrity)
    except Exception as exc:  # never crash the GUI
        report.ok = False
        report.add(f"Error while checking this log: {exc.__class__.__name__}: {exc}\n", BAD)
        report.add(traceback.format_exc(limit=3) + "\n")
    return report


def _score(path: Path, report: Report, integrity: bool) -> None:
    from heybrochecklog.score import score_log

    log = score_log(path, True, integrity)
    if log.get("unrecognized"):
        report.ok = False
        report.add("Log is unrecognized: ", BAD)
        report.add(f"{log['unrecognized']}\n", BAD)
        contents = log.get("contents") or ""
        if contents.strip():
            report.add("\nLog contents:\n\n", LABEL)
            report.add(html.unescape(contents))
        return
    if log.get("flagged"):
        report.add("Log is flagged: ", BAD)
        report.add(f"{log['flagged']}\n\n", BAD)
    report.add("Disc name: ", LABEL)
    report.add(f"{log.get('name')}\n\n", Style(COLORS["log4"]))
    report.score = log.get("score")
    report.add("Score: ", LABEL)
    report.add(f"{report.score}\n", _score_style(report.score))
    deductions = log.get("deductions") or []
    if deductions:
        report.add("\nDeductions:\n", LABEL)
        for deduction in deductions:
            text = deduction[0] if isinstance(deduction, (list, tuple)) else deduction
            report.add("  >>  ", LABEL)
            report.add(f"{text}\n", WARN)
    report.add("\n\nStylized Log:\n\n", LABEL)
    report.add_markup(log.get("contents") or "")
    if not report.text.endswith("\n"):
        report.add("\n")


def _translate(path: Path, report: Report) -> None:
    from heybrochecklog.translate import translate_log

    log = translate_log(path)
    if log.get("unrecognized"):
        report.ok = False
        report.add("Failed to recognize log. ", BAD)
        report.add(f"{log['unrecognized']}\n", BAD)
        return
    if log.get("language") == "english":
        report.add("Log is already in English!\n", GOOD)
        return
    report.add("Original language: ", LABEL)
    report.add(f"{str(log.get('language')).title()}\n", HEADER)
    report.add("---------------------------------------------------\n\n")
    report.add(html.unescape(log.get("log") or "") + "\n")


def to_html(reports: list[Report], title: str = "hbcl report") -> str:
    from .render import BACKGROUND, FOREGROUND

    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        f"<title>{html.escape(title)}</title>",
        f"<style>body{{background:{BACKGROUND};color:{FOREGROUND};}}"
        "pre{font-family:Consolas,'DejaVu Sans Mono',monospace;font-size:13px;}</style>",
        "</head><body><pre>",
    ]
    for i, rep in enumerate(reports):
        if i:
            parts.append("\n" + "=" * 80 + "\n\n")
        for text, style in rep.segments:
            esc = html.escape(text)
            css = []
            if style.color:
                css.append(f"color:{style.color}")
            if style.bold:
                css.append("font-weight:bold")
            parts.append(f"<span style='{';'.join(css)}'>{esc}</span>" if css else esc)
    parts.append("</pre></body></html>\n")
    return "".join(parts)

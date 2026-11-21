"""Turn hbcl's HTML markup into plain text segments with style classes.

hbcl marks up a log by HTML-escaping every line and wrapping interesting
parts in ``<span class="...">`` (possibly nested) and ``<strong>`` tags.
This module parses that markup without any GUI dependency so it can be
unit tested; the Tk front end maps the classes to text tags.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from html.parser import HTMLParser

# Colours used by the GUI (dark theme). Keys are hbcl markup classes.
COLORS = {
    "good": "#5fd35f",  # green: correct settings / accurate rips
    "badish": "#f0a830",  # orange-yellow: warnings / moderate deductions
    "bad": "#ff5555",  # red: bad settings / errors
    "log1": "#c3e88d",  # ripper version + date (yellow-green, like OPS)
    "log3": "#e6c84d",  # file names / paths (yellow)
    "log4": "#59b6ff",  # neutral values, album line, block headers (blue)
    "log5": "#ffffff",  # setting names (bright white, lowest priority)
}
# Classes rendered in bold (matches the old logchecker CSS where
# good/bad/badish are bold).
BOLD_CLASSES = {"good", "badish", "bad", "strong"}
# log5 only supplies a colour if nothing else in the span stack does.
LOW_PRIORITY = {"log5"}

BACKGROUND = "#1e1e1e"
FOREGROUND = "#d4d4d4"


@dataclass(frozen=True)
class Style:
    color: str | None = None
    bold: bool = False

    @property
    def tag(self) -> str:
        return f"fg:{self.color or 'default'}:{'b' if self.bold else 'n'}"


def resolve_style(stack: list[set[str]]) -> Style:
    """Compute the effective style for text inside a stack of class sets.

    The innermost span with a (non low-priority) colour wins, mimicking CSS.
    """
    color = None
    for classes in reversed(stack):
        for cls in sorted(classes):
            if cls in COLORS and cls not in LOW_PRIORITY:
                color = COLORS[cls]
                break
        if color:
            break
    if color is None:
        for classes in reversed(stack):
            hit = [c for c in classes if c in LOW_PRIORITY]
            if hit:
                color = COLORS[hit[0]]
                break
    bold = any(cls in BOLD_CLASSES for classes in stack for cls in classes)
    return Style(color, bold)


class _MarkupParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[set[str]] = []
        self.segments: list[tuple[str, Style]] = []

    def handle_starttag(self, tag, attrs):
        if tag == "span":
            classes = set((dict(attrs).get("class") or "").split())
            self.stack.append(classes)
        elif tag in ("strong", "b"):
            self.stack.append({"strong"})
        elif tag == "br":
            self.handle_data("\n")
        else:
            # Unknown tag: keep it visible as text rather than dropping it.
            self.handle_data(self.get_starttag_text() or "")

    def handle_endtag(self, tag):
        if tag in ("span", "strong", "b"):
            if self.stack:
                self.stack.pop()
        elif tag != "br":
            self.handle_data(f"</{tag}>")

    def handle_data(self, data):
        if not data:
            return
        style = resolve_style(self.stack)
        if self.segments and self.segments[-1][1] == style:
            self.segments[-1] = (self.segments[-1][0] + data, style)
        else:
            self.segments.append((data, style))


# hbcl's substitute() can occasionally insert a span *inside* a span tag it
# created earlier (seen in EAC 0.95 track headers), e.g.
#   <sp<span class="log5">an class="log4 log5">Track  1</span></span>
# Move the stray opening tag behind the broken tag so the markup is valid:
#   <span class="log4 log5"><span class="log5">Track  1</span></span>
_BROKEN_TAG = re.compile(r'<([a-z]*)(<span class="[^"<>]*">)([a-z]*)((?: [^<>]*)?>)')


def repair_markup(markup: str) -> str:
    def fix(m: re.Match) -> str:
        if m.group(1) + m.group(3) in ("span", "strong"):
            return "<" + m.group(1) + m.group(3) + m.group(4) + m.group(2)
        return m.group(0)

    return _BROKEN_TAG.sub(fix, markup)


def parse_markup(markup: str) -> list[tuple[str, Style]]:
    """Parse hbcl markup into ``(text, Style)`` segments (entities unescaped)."""
    markup = repair_markup(markup)
    parser = _MarkupParser()
    try:
        parser.feed(markup)
        parser.close()
    except Exception:  # pragma: no cover - defensive, never crash the GUI
        return [(html.unescape(markup), Style())]
    return parser.segments


def plain_text(markup: str) -> str:
    return "".join(text for text, _ in parse_markup(markup))

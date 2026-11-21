"""Logic tests (no display needed). Point HBCL_TESTS at hbcl's tests/logs folder
to also run every sample log through the checker."""

import html
import os
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hbcl_gui.core import check_log, to_html  # noqa: E402
from hbcl_gui.render import COLORS, parse_markup, plain_text, repair_markup  # noqa: E402

LOGS = Path(os.environ.get("HBCL_TESTS", "../hbcl/tests/logs"))
SAMPLES = sorted(LOGS.rglob("*.log")) if LOGS.is_dir() else []


def test_nested_innermost_wins_and_entities():
    segs = parse_markup(
        '<span class="good">EAC <span class="log5">from 1 &amp; 2</span></span>'
        ' <span class="bad">x &lt;y&gt;</span>'
    )
    assert "".join(t for t, _ in segs) == "EAC from 1 & 2 x <y>"
    by_text = {t: s for t, s in segs}
    # log5 is low priority -> the whole thing stays green+bold (merged segment)
    assert by_text["EAC from 1 & 2"].color == COLORS["good"]
    assert by_text["EAC from 1 & 2"].bold
    assert by_text["x <y>"].color == COLORS["bad"]


def test_repair_broken_upstream_markup():
    broken = '<sp<span class="log5">an class="log4 log5">Track  <span class="log4 log1">1</span></span></span>'
    segs = parse_markup(broken)
    assert "".join(t for t, _ in segs) == "Track  1"


def test_multi_class_and_strong():
    segs = parse_markup('<span class="log4 log5">TOC</span><strong>!</strong>')
    assert segs[0][1].color == COLORS["log4"]
    assert segs[1][1].bold


def test_missing_file_does_not_raise(tmp_path):
    rep = check_log(tmp_path / "nope.log")
    assert not rep.ok and "does not exist" in rep.text


def test_binary_garbage_does_not_raise(tmp_path):
    p = tmp_path / "garbage.log"
    p.write_bytes(os.urandom(4096))
    rep = check_log(p)
    assert not rep.ok


@pytest.mark.skipif(not SAMPLES, reason="hbcl sample logs not found")
@pytest.mark.parametrize("log", SAMPLES, ids=lambda p: str(p.relative_to(LOGS)))
@pytest.mark.parametrize("translate", [False, True])
def test_sample_logs(log, translate):
    rep = check_log(log, translate=translate, integrity=True)
    assert rep.text.startswith("Log: ")
    assert "Error while checking" not in rep.text
    if not translate and rep.ok:
        assert isinstance(rep.score, int)
        assert "Stylized Log:" in rep.text
    to_html([rep])


@pytest.mark.skipif(not SAMPLES, reason="hbcl sample logs not found")
@pytest.mark.parametrize("log", SAMPLES, ids=lambda p: str(p.relative_to(LOGS)))
def test_markup_roundtrip(log):
    from heybrochecklog.score import score_log

    contents = score_log(log, True)["contents"]
    fixed = repair_markup(contents)
    expected = html.unescape(re.sub(r"</?(span|strong)[^>]*>", "", fixed))
    text = plain_text(contents)
    assert text == expected
    assert 'class="' not in text and "<span" not in text

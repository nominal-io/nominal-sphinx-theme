import re

import nominal_sphinx_theme
from test_header_path import build

# the theme's commit in the footer (templates/partials/site-foot.html)
STAMP = re.compile(r'<p class="nominal-theme-commit" data-commit="([0-9a-f]{40})">\s*Theme <a href="([^"]*)"><code>([0-9a-f]+)</code></a>')


def test_the_footer_shows_the_themes_commit(tmp_path, monkeypatch):
    commit = "1101d9b30cb01206073e40e935982ba5183ab272"
    monkeypatch.setattr(nominal_sphinx_theme, "theme_commit", lambda: commit)
    out = build(tmp_path)
    for page in (out / "index.html", out / "guide" / "index.html"):
        assert STAMP.search(page.read_text()).groups() == (
            commit,
            f"https://github.com/nominal-io/nominal-sphinx-theme/commit/{commit}",
            "1101d9b",
        )


def test_no_stamp_without_a_commit(tmp_path, monkeypatch):
    monkeypatch.setattr(nominal_sphinx_theme, "theme_commit", lambda: None)
    out = build(tmp_path)
    assert "nominal-theme-commit" not in (out / "index.html").read_text()


def test_a_checkout_reads_its_own_head():
    nominal_sphinx_theme.theme_commit.cache_clear()
    assert re.fullmatch(r"[0-9a-f]{40}", nominal_sphinx_theme.theme_commit() or "")

import io
import re
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

# the DOCS and DEVELOPERS links after the Nominal logo (templates/nominal/path.html)
LINK = re.compile(r'<a href="([^"]*)" title="Nominal (docs|developer docs)"([^>]*)>')


def build(tmp_path: Path, conf: str = "") -> Path:
    """Build a small project with a page below its home: its output folder."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "conf.py").write_text(f'extensions = ["myst_parser", "nominal_sphinx_theme"]\nhtml_theme = "shibuya"\n{conf}')
    (src / "index.md").write_text("# Home\n\n```{toctree}\n:hidden:\n\nguide\n```\n")
    (src / "guide.md").write_text("# Guide\n")
    warnings = io.StringIO()
    with docutils_namespace():
        app = Sphinx(src, src, tmp_path / "out", tmp_path / "doctrees", "dirhtml", status=None, warning=warnings, warningiserror=True)
        app.build()
    assert app.statuscode == 0, warnings.getvalue()
    return tmp_path / "out"


def links(page: Path) -> dict[str, tuple[str, str]]:
    return {title: (href, attrs) for href, title, attrs in LINK.findall(page.read_text())}


def test_docs_opens_nominal_docs_in_a_new_tab_and_developers_the_hub(tmp_path):
    out = build(tmp_path)
    assert links(out / "index.html") == {
        "docs": ("https://dev.nominal.io/", ' target="_blank" rel="noopener noreferrer"'),
        "developer docs": ("../", ""),
    }
    assert links(out / "guide" / "index.html")["developer docs"] == ("../../", "")


def test_the_links_can_be_set(tmp_path):
    out = build(tmp_path, 'nominal_docs_url = "https://example.com/docs/"\nnominal_hub_url = "https://dev.nominal.io/"\n')
    assert links(out / "index.html") == {
        "docs": ("https://example.com/docs/", ' target="_blank" rel="noopener noreferrer"'),
        "developer docs": ("https://dev.nominal.io/", ""),
    }

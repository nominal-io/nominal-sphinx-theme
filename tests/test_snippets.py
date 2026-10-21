import base64
import io
from pathlib import Path

import pytest
from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

from nominal_sphinx_theme import snippet_directive

# a 1x1 PNG
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)

CONF = """
extensions = ["myst_parser", "nominal_sphinx_theme"]
myst_enable_extensions = ["colon_fence"]
html_theme = "shibuya"
"""


@pytest.fixture
def snippets(tmp_path, monkeypatch):
    root = tmp_path / "snippets"
    (root / "demo").mkdir(parents=True)
    (root / "demo" / "shot.png").write_bytes(PNG)
    (root / "demo" / "steps.md").write_text(
        "Snippet intro.\n\n## Snippet heading\n\n![A screenshot](shot.png)\n\n"
        ":::{figure} shot.png\nA figure\n:::\n"
    )
    monkeypatch.setattr(snippet_directive, "SNIPPETS", root)
    return root


def build(tmp_path: Path, page: str, conf: str = CONF) -> tuple[Path, int, str]:
    """Build a one-page project with warnings as errors: its output folder, status and warnings."""
    src = tmp_path / "src"
    src.mkdir(exist_ok=True)
    (src / "conf.py").write_text(conf)
    (src / "index.md").write_text(page)
    out = tmp_path / "out"
    warnings = io.StringIO()
    with docutils_namespace():
        app = Sphinx(src, src, out, tmp_path / "doctrees", "dirhtml", status=None, warning=warnings, warningiserror=True)
        app.build()
    return out, app.statuscode, warnings.getvalue()


def test_renders_snippet_with_images(tmp_path, snippets):
    out, status, warnings = build(tmp_path, "# Page\n\n```{nominal-snippet} demo/steps\n```\n")
    assert status == 0, warnings
    html = (out / "index.html").read_text()
    assert html.index("Snippet intro.") < html.index('id="snippet-heading"')
    assert html.count('src="_images/shot.png"') == 2
    assert (out / "_images" / "shot.png").read_bytes() == PNG
    copies = tmp_path / "src" / "_nominal_snippets"
    assert (copies / "demo" / "shot.png").read_bytes() == PNG
    assert (copies / ".gitignore").read_text() == "*\n"


def test_unknown_snippet_fails_the_build(tmp_path, snippets):
    _, status, warnings = build(tmp_path, "# Page\n\n```{nominal-snippet} demo/missing\n```\n")
    assert status == 1
    assert "unknown snippet 'demo/missing'" in warnings


def test_shipped_snippets_build(tmp_path):
    # every snippet the theme ships, with the extensions the README says they need
    names = sorted(p.relative_to(snippet_directive.SNIPPETS).with_suffix("").as_posix() for p in snippet_directive.SNIPPETS.rglob("*.md"))
    assert names
    page = "# Page\n\n" + "".join(f"```{{nominal-snippet}} {name}\n```\n\n" for name in names)
    conf = CONF.replace('"myst_parser",', '"myst_parser", "sphinx_design",').replace('["colon_fence"]', '["colon_fence", "attrs_block"]')
    out, status, warnings = build(tmp_path, page, conf)
    assert status == 0, warnings
    for image in snippet_directive.SNIPPETS.rglob("*.png"):
        assert (out / "_images" / image.name).exists()


def test_builds_without_snippets(tmp_path, monkeypatch):
    monkeypatch.setattr(snippet_directive, "SNIPPETS", tmp_path / "none")
    _, status, warnings = build(tmp_path, "# Page\n")
    assert status == 0, warnings
    assert not (tmp_path / "src" / "_nominal_snippets").exists()

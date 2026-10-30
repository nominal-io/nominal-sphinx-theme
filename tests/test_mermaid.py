import io
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

CONF = """
extensions = ["myst_parser", "sphinxcontrib.mermaid", "nominal_sphinx_theme"]
myst_fence_as_directive = ["mermaid"]
html_theme = "shibuya"
"""

PAGE = """# Page

```mermaid
---
config:
  layout: elk
name: stack-diagram
---
flowchart TB
  a --> b
```
"""


def build(tmp_path: Path, conf: str = CONF) -> tuple[Sphinx, str]:
    """Build a one-page project with warnings as errors: the app and its HTML."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "conf.py").write_text(conf)
    (src / "index.md").write_text(PAGE)
    with docutils_namespace():
        app = Sphinx(src, src, tmp_path / "out", tmp_path / "doctrees", "dirhtml", status=None, warning=io.StringIO(), warningiserror=True)
        app.build()
    return app, (tmp_path / "out" / "index.html").read_text()


def test_front_matter_becomes_options(tmp_path):
    app, html = build(tmp_path)
    assert app.statuscode == 0
    assert 'id="stack-diagram"' in html
    # sphinxcontrib-mermaid writes the :config: option back as front matter, for Mermaid
    assert "config:\n  layout: elk" in html


def test_not_loaded_without_mermaid(tmp_path):
    # without sphinxcontrib-mermaid, the block is code and keeps its front matter as written
    conf = 'extensions = ["myst_parser", "nominal_sphinx_theme"]\nhtml_theme = "shibuya"\n'
    app, html = build(tmp_path, conf)
    assert "nominal_sphinx_theme.mermaid_frontmatter" not in app.extensions
    assert "layout" in html and ":config:" not in html

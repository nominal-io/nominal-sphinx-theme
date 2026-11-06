import io
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

CONF = """
extensions = ["myst_parser", "nominal_sphinx_theme"]
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


def test_fence_is_a_diagram(tmp_path):
    # the theme sets up sphinxcontrib-mermaid, and makes a ```mermaid fence its directive
    app, html = build(tmp_path)
    assert app.statuscode == 0
    assert "sphinxcontrib.mermaid" in app.extensions
    assert 'class="mermaid"' in html
    assert app.config.mermaid_height == "auto"


def test_front_matter_becomes_options(tmp_path):
    app, html = build(tmp_path)
    assert 'id="stack-diagram"' in html
    # sphinxcontrib-mermaid writes the :config: option back as front matter, for Mermaid
    assert "config:\n  layout: elk" in html


def test_listed_extension_and_conf_py_win(tmp_path):
    # a project that lists sphinxcontrib.mermaid, as before the theme set it up, still builds
    conf = CONF.replace('"myst_parser"', '"myst_parser", "sphinxcontrib.mermaid"') + 'mermaid_height = "300px"\n'
    app, html = build(tmp_path, conf)
    assert app.statuscode == 0
    assert app.config.mermaid_height == "300px"

import io
import re
from pathlib import Path

import pytest
from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

from nominal_sphinx_theme import DOCS_SITES, intersphinx

CONF = """
extensions = ["myst_parser", "nominal_sphinx_theme"]
html_theme = "shibuya"
"""

# json.dumps is documented on the page, so its links resolve without an intersphinx inventory
PAGE = """# Page

```{py:function} json.dumps(obj)
```

```python
import json
json.dumps({})
```

A later block, which knows `json` from the one before:

```python
json.dumps([])
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


def links(html: str) -> list[str]:
    return re.findall(r'<a class="sphinx-codeautolink-a"[^>]*href="([^"]*)"', html)


def test_code_links_to_docs(tmp_path):
    # the theme sets up sphinx-codeautolink and intersphinx, with no entries in extensions
    app, html = build(tmp_path)
    assert app.statuscode == 0
    assert {"sphinx_codeautolink", "sphinx.ext.intersphinx"} <= set(app.extensions)
    # json.dumps links in both blocks: the second knows the import from the first
    assert links(html).count("#json.dumps") == 2


def test_conf_py_wins(tmp_path):
    # without concatenation, the second block doesn't know json, so only the first links
    app, html = build(tmp_path, CONF + "codeautolink_concat_default = False\n")
    assert links(html).count("#json.dumps") == 1


def test_intersphinx():
    assert intersphinx("nominal", "instro") == {
        "nominal": (DOCS_SITES["nominal"], None),
        "instro": (DOCS_SITES["instro"], None),
    }
    with pytest.raises(ValueError, match="nominal-client"):
        intersphinx("nominal-client")

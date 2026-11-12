import re
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

PAGE = """# Page

## Section

```python
import json
```

```text
a prompt
```
"""


def build(tmp_path: Path) -> Path:
    src = tmp_path / "src"
    src.mkdir()
    (src / "conf.py").write_text('extensions = ["myst_parser", "nominal_sphinx_theme"]\nhtml_theme = "shibuya"\n')
    (src / "index.md").write_text(PAGE)
    with docutils_namespace():
        Sphinx(src, src, tmp_path / "out", tmp_path / "doctrees", "dirhtml", status=None, warningiserror=True).build()
    return tmp_path / "out"


def test_the_page_has_what_the_fold_all_script_attaches_to(tmp_path):
    """nominal.js adds "Fold all code" before the "On this page" list, and folds `main` code blocks."""
    html = (build(tmp_path) / "index.html").read_text()
    assert '<div class="localtoc"><h3>On this page</h3>' in html
    main = html[html.index("<main") :]
    assert len(re.findall(r'<div class="highlight-(?:python|text)[ "]', main)) == 2


def test_the_fold_all_script_and_style_ship_with_the_theme(tmp_path):
    static = build(tmp_path) / "_static"
    script, style = (static / "nominal.js").read_text(), (static / "nominal.css").read_text()
    assert "nominal-fold-all" in script and ".nominal-fold-all" in style
    assert "nominal-fold-one" in script and ".nominal-fold-one" in style

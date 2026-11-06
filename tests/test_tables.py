import io
import re
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

PAGE = """# Page

| Name | Count | Mid |
| :--- | ---: | :---: |
| a | 1 | x |
"""


def test_alignment_classes_have_rules(tmp_path: Path):
    """Each alignment class MyST writes for a table column has a rule in the theme's stylesheet."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "conf.py").write_text('extensions = ["myst_parser", "nominal_sphinx_theme"]\nhtml_theme = "shibuya"\n')
    (src / "index.md").write_text(PAGE)
    with docutils_namespace():
        app = Sphinx(src, src, tmp_path / "out", tmp_path / "doctrees", "html", status=None, warning=io.StringIO(), warningiserror=True)
        app.build()
    html = (tmp_path / "out" / "index.html").read_text()
    css = (tmp_path / "out" / "_static" / "nominal.css").read_text()
    for side in ("left", "right", "center"):
        assert f'<td class="text-{side}">' in html
        rule = re.search(rf"\.yue td\.text-{side} \{{\s*text-align: {side};", css)
        assert rule, side

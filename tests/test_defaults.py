import io
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

CONF = """
project = "Demo"
extensions = ["myst_parser", "nominal_sphinx_theme"]
html_theme = "shibuya"
"""

PAGE = """# Page

See [the section](#a-section) and [Nominal](https://nominal.io/).

:::{note}
A note.
:::

## A section
"""


def build(tmp_path: Path, conf: str = CONF, overrides: dict | None = None) -> tuple[Sphinx, Path]:
    """Build a one-page project with warnings as errors: the app and its output folder."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "conf.py").write_text(conf)
    (src / "index.md").write_text(PAGE)
    out = tmp_path / "out"
    with docutils_namespace():
        app = Sphinx(src, src, out, tmp_path / "doctrees", "dirhtml", confoverrides=overrides, status=None, warning=io.StringIO(), warningiserror=True)
        app.build()
    return app, out


def test_defaults(tmp_path):
    # the heading link and the note need myst_heading_anchors and colon_fence; a warning fails the build
    app, out = build(tmp_path)
    html = (out / "index.html").read_text()
    assert app.statuscode == 0
    assert 'href="#a-section"' in html
    assert 'class="admonition note"' in html
    assert 'class="reference external" href="https://nominal.io/" rel="noreferer noopener" target="_blank"' in html
    # the root page's title is html_title alone
    assert "<title>Demo</title>" in html
    # Sphinx makes _sources either way; html_copy_source decides whether the pages go in it
    assert not [f for f in (out / "_sources").rglob("*") if f.is_file()]


def test_conf_py_wins(tmp_path):
    conf = CONF + "html_copy_source = True\nmyst_links_external_new_tab = False\nhtml_title = 'Other'\n"
    app, out = build(tmp_path, conf)
    html = (out / "index.html").read_text()
    assert 'class="reference external" href="https://nominal.io/">' in html
    assert "<title>Other</title>" in html
    assert (out / "_sources" / "index.md.txt").is_file()


def test_command_line_wins(tmp_path):
    app, out = build(tmp_path, overrides={"myst_links_external_new_tab": False})
    assert app.config.myst_links_external_new_tab is False
    assert app.config.myst_heading_anchors == 6

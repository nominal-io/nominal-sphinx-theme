import pytest
from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

from nominal_sphinx_theme import output_ids

REAL = "1b4e28ba-2fa1-11d2-883f-0016d3cca427"

CONF = """
extensions = ["nominal_sphinx_theme"]
html_theme = "shibuya"

from docutils import nodes
from docutils.parsers.rst import Directive


class CellOutput(Directive):
    # stands in for myst-nb, which marks a cell's output with the class cell_output
    has_content = True

    def run(self):
        node = nodes.container(classes=["cell_output"])
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


def setup(app):
    app.add_directive("cell-output", CellOutput)
"""

# Shaped like myst-nb's output: a cell's source, then its output as text and as raw HTML.
PAGE = f"""
Page
====

.. container:: cell_input

   .. code-block:: python

      run = client.get_run("ri.scout.example.run.{REAL}")

.. cell-output::

   .. code-block:: text

      Run(rid='ri.scout.example.run.{REAL}')

   .. raw:: html

      <a href="https://app.example.com/runs/{REAL}" data-copy="{REAL.upper()}">run</a>
"""


def _build(tmp_path, monkeypatch, ci: str | None, conf: str = CONF) -> str:
    """The HTML of a page with a notebook-style cell, built with the CI environment variable set to ``ci``."""
    if ci is None:
        monkeypatch.delenv("CI", raising=False)
    else:
        monkeypatch.setenv("CI", ci)
    (tmp_path / "conf.py").write_text(conf)
    (tmp_path / "index.rst").write_text(PAGE)
    with docutils_namespace():
        app = Sphinx(tmp_path, tmp_path, tmp_path / "out", tmp_path / "doctrees", "dirhtml", status=None, warning=None)
        app.build()
    return (tmp_path / "out" / "index.html").read_text().lower()


@pytest.mark.parametrize("ci", ["true", "1", "yes"])
def test_ci_scrambles_output_ids(tmp_path, monkeypatch, ci):
    """On CI, every UUID in an output, in text or HTML and in any case, becomes the same stand-in."""
    html = _build(tmp_path, monkeypatch, ci)
    stand_in = output_ids._stand_in(output_ids.UUID.search(REAL))
    assert html.count(stand_in) == 3
    assert html.count(REAL) == 1  # the code shown on the page stays as written


def test_stand_ins_are_stable_across_builds(tmp_path, monkeypatch):
    """The same UUID gets the same stand-in every build, so rebuilding doesn't change pages."""
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    first = _build(tmp_path / "a", monkeypatch, "1")
    second = _build(tmp_path / "b", monkeypatch, "1")
    assert first == second


@pytest.mark.parametrize("ci", [None, "", "0", "false", "False"])
def test_local_build_keeps_output_ids(tmp_path, monkeypatch, ci):
    """Without CI, outputs are published as they are, so their links and copy buttons work."""
    assert _build(tmp_path, monkeypatch, ci).count(REAL) == 4


def test_conf_can_scramble_locally(tmp_path, monkeypatch):
    html = _build(tmp_path, monkeypatch, None, CONF + "nominal_scramble_output_ids = True\n")
    assert html.count(REAL) == 1


def test_conf_can_keep_ids_on_ci(tmp_path, monkeypatch):
    html = _build(tmp_path, monkeypatch, "1", CONF + "nominal_scramble_output_ids = False\n")
    assert html.count(REAL) == 4

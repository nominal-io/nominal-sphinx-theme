from types import SimpleNamespace

import pytest
from docutils import nodes
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser
from docutils.utils import new_document
from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

from nominal_sphinx_theme import output_ids

REAL = "1b4e28ba-2fa1-11d2-883f-0016d3cca427"


def _page() -> nodes.document:
    """A page shaped like myst-nb's: a cell's source, then its output as text and as raw HTML."""
    document = new_document("<test>", get_default_settings(Parser))
    source = nodes.container(classes=["cell_input"])
    source += nodes.literal_block(text=f'run = client.get_run("ri.scout.example.run.{REAL}")')
    output = nodes.container(classes=["cell_output"])
    output += nodes.literal_block(text=f"Run(rid='ri.scout.example.run.{REAL}')")
    output += nodes.raw(
        "", f'<a href="https://app.example.com/runs/{REAL}" data-copy="{REAL.upper()}">run</a>', format="html"
    )
    document += [source, output]
    return document


def _scramble(document: nodes.document, enabled: bool = True) -> None:
    app = SimpleNamespace(config=SimpleNamespace(nominal_scramble_output_ids=enabled))
    output_ids._scramble_output_ids(app, document)


def test_outputs_get_one_stand_in_per_uuid():
    """Each UUID in an output, in text or HTML and in any case, becomes the same stand-in."""
    document = _page()
    _scramble(document)
    source, output = document.children
    stand_in = output_ids.UUID.search(output.astext()).group()
    assert stand_in != REAL
    assert REAL not in output.astext().lower()
    assert output.astext().count(stand_in) == 3
    assert REAL in source.astext()  # the code shown on the page stays as written


def test_stand_ins_are_stable_across_builds():
    """The same UUID gets the same stand-in every build, so rebuilding doesn't change pages."""
    first, second = _page(), _page()
    _scramble(first)
    _scramble(second)
    assert first.astext() == second.astext()


def test_setting_off_keeps_outputs():
    """With nominal_scramble_output_ids off, outputs are published as they are."""
    document = _page()
    _scramble(document, enabled=False)
    assert document.children[1].astext().count(REAL) == 2


CONF = """
extensions = ["nominal_sphinx_theme"]
html_theme = "shibuya"
"""


def _option(tmp_path, monkeypatch, ci: str | None, conf: str = CONF) -> bool:
    """The option's value in a project built with the CI environment variable set to ``ci``."""
    if ci is None:
        monkeypatch.delenv("CI", raising=False)
    else:
        monkeypatch.setenv("CI", ci)
    (tmp_path / "conf.py").write_text(conf)
    (tmp_path / "index.md").write_text("# Page\n")
    with docutils_namespace():
        app = Sphinx(tmp_path, tmp_path, tmp_path / "out", tmp_path / "doctrees", "dirhtml", status=None, warning=None)
    return app.config.nominal_scramble_output_ids


@pytest.mark.parametrize("ci", ["true", "1", "yes"])
def test_default_scrambles_on_ci(tmp_path, monkeypatch, ci):
    assert _option(tmp_path, monkeypatch, ci) is True


@pytest.mark.parametrize("ci", [None, "", "0", "false", "False"])
def test_default_keeps_ids_locally(tmp_path, monkeypatch, ci):
    assert _option(tmp_path, monkeypatch, ci) is False


def test_conf_can_scramble_locally(tmp_path, monkeypatch):
    assert _option(tmp_path, monkeypatch, None, CONF + "nominal_scramble_output_ids = True\n") is True


def test_conf_can_keep_ids_on_ci(tmp_path, monkeypatch):
    assert _option(tmp_path, monkeypatch, "true", CONF + "nominal_scramble_output_ids = False\n") is False

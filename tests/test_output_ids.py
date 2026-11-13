from types import SimpleNamespace

import pytest
from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

from nominal_sphinx_theme import output_ids

UUID = "123e4567-e89b-42d3-a456-426614174000"
CONF = """
extensions = ["nominal_sphinx_theme"]
html_theme = "shibuya"
"""


def default_for(tmp_path, monkeypatch, ci: str | None, conf: str = CONF) -> bool:
    """The value of the option in a project built with the CI environment variable set to ``ci``."""
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
def test_scrambles_on_ci(tmp_path, monkeypatch, ci):
    assert default_for(tmp_path, monkeypatch, ci) is True


@pytest.mark.parametrize("ci", [None, "", "0", "false", "False"])
def test_keeps_ids_locally(tmp_path, monkeypatch, ci):
    assert default_for(tmp_path, monkeypatch, ci) is False


def test_conf_can_scramble_locally(tmp_path, monkeypatch):
    assert default_for(tmp_path, monkeypatch, None, CONF + "nominal_scramble_output_ids = True\n") is True


def test_conf_can_keep_ids_on_ci(tmp_path, monkeypatch):
    assert default_for(tmp_path, monkeypatch, "true", CONF + "nominal_scramble_output_ids = False\n") is False


def output_text(scramble: bool) -> str:
    """Run the extension on a cell output holding a UUID, and return the text that results."""
    doctree = nodes.document(None, None)  # type: ignore[arg-type]
    output = nodes.container(classes=["cell_output"])
    output += nodes.paragraph("", UUID)
    doctree += output
    app = SimpleNamespace(config=SimpleNamespace(nominal_scramble_output_ids=scramble))
    output_ids._scramble_output_ids(app, doctree)  # type: ignore[arg-type]
    return doctree.astext()


def test_scrambling_replaces_the_uuid():
    scrambled = output_text(True)
    assert UUID not in scrambled and len(scrambled) == len(UUID)


def test_not_scrambling_keeps_the_uuid():
    assert output_text(False) == UUID

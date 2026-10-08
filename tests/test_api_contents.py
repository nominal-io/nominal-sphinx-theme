"""API navigation stays useful without hiding reference content."""

import pickle
import subprocess
import sys
from pathlib import Path

from docutils import nodes


def test_api_contents_lists_classes_functions_and_methods(tmp_path: Path) -> None:
    """Omit attributes, properties, and aliases from the TOC while retaining their targets."""
    source = tmp_path / "docs"
    source.mkdir()
    theme = Path(__file__).resolve().parents[1] / "src"
    (source / "conf.py").write_text(
        f"import sys\nsys.path[:0] = [{str(theme)!r}, {str(tmp_path)!r}]\n"
        "extensions = ['sphinx.ext.autodoc', 'nominal_sphinx_theme']\n"
        "html_theme = 'shibuya'\n"
        "autodoc_default_options = {'members': True, 'undoc-members': True}\n",
        encoding="utf-8",
    )
    (source / "index.rst").write_text(
        "API\n===\n\n.. autoclass:: fixture_api.Book\n\n"
        ".. autofunction:: fixture_api.open_book\n\n.. autodata:: fixture_api.Alias\n",
        encoding="utf-8",
    )
    (tmp_path / "fixture_api.py").write_text(
        '''class Book:
    """A public resource."""
    value: str

    @property
    def title(self) -> str:
        """The resource title."""
        return self.value

    def read(self) -> str:
        """Read the resource."""
        return self.value


def open_book() -> Book:
    """Open a resource."""
    return Book()


Alias = str
"""A public alias."""
''',
        encoding="utf-8",
    )
    output = tmp_path / "html"
    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-W", "-E", "-b", "html", str(source), str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    env = pickle.loads((output / ".doctrees/environment.pickle").read_bytes())
    targets = {node.get("anchorname") for node in env.tocs["index"].findall(nodes.reference)}
    assert "#fixture_api.Book" in targets
    assert "#fixture_api.Book.read" in targets
    assert "#fixture_api.open_book" in targets
    for name in ["fixture_api.Book.value", "fixture_api.Book.title", "fixture_api.Alias"]:
        assert "#" + name not in targets
        assert f'id="{name}"' in (output / "index.html").read_text(encoding="utf-8")

import io
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

from nominal_sphinx_theme.docstring_fences import convert_fences

MODULE = '''
def read(path):
    """Read a file.

    Example:
        ```python
        read("data.avro")
        ```

    Args:
        path: The file to read.
    """
'''

CONF = """
import sys
sys.path.insert(0, {src!r})
extensions = ["sphinx.ext.napoleon", "nominal_sphinx_theme"{fences}]
html_theme = "shibuya"
"""


def build(tmp_path: Path, fences: bool) -> tuple[str, str]:
    """Build a page that documents read() with autodoc: its HTML and the build's warnings."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "fenced.py").write_text(MODULE)
    extra = ', "nominal_sphinx_theme.docstring_fences"' if fences else ', "sphinx.ext.autodoc"'
    (src / "conf.py").write_text(CONF.format(src=str(src), fences=extra))
    (src / "index.rst").write_text("Page\n====\n\n.. autofunction:: fenced.read\n")
    warnings = io.StringIO()
    with docutils_namespace():
        app = Sphinx(src, src, tmp_path / "out", tmp_path / "doctrees", "dirhtml", status=None, warning=warnings)
        app.build()
    return (tmp_path / "out" / "index.html").read_text(), warnings.getvalue()


def test_fence_becomes_code_block():
    lines = ["Example:", "    ```python", "    read('x')", "", "    more()", "    ```", "Args:"]
    convert_fences(lines)
    assert lines == ["Example:", "    .. code-block:: python", "", "        read('x')", "", "        more()", "", "Args:"]


def test_fence_without_language_is_text():
    lines = ["```", "plain", "```"]
    convert_fences(lines)
    assert lines[0] == ".. code-block:: text"


def test_docstring_fence_renders_as_code(tmp_path):
    html, warnings = build(tmp_path, fences=True)
    assert warnings == ""
    assert "highlight-python" in html


def test_off_unless_listed(tmp_path):
    # without the module in extensions, the theme leaves the fence as it is: no code block
    html, _ = build(tmp_path, fences=False)
    assert "highlight-python" not in html

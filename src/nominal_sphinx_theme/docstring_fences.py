"""Opt-in: turn Markdown code fences in docstrings into code blocks.

autodoc and sphinx-autoapi read docstrings as reStructuredText, where a ``` fence is broken inline
markup. A repo whose docstrings put examples in fences adds this module to `extensions`, unlike the
theme's other modules, which are always on. Each fence becomes a `.. code-block::` before Napoleon
reads the docstring's sections, and the same happens to sphinx-click's command descriptions when
the repo loads sphinx-click.
"""

import re
from typing import Any

from sphinx.application import Sphinx
from sphinx.config import Config

CODE_FENCE = re.compile(
    r"^(?P<indent> *)```(?P<language>[\w.+-]*)[ \t]*\n"
    r"(?P<code>(?:(?P=indent)[^\n]*\n|[ \t]*\n)*?)^(?P=indent)```[ \t]*$",
    re.MULTILINE,
)


def _code_block(match: re.Match[str]) -> str:
    body = "\n".join("    " + line if line.strip() else "" for line in match["code"].splitlines())
    return f"{match['indent']}.. code-block:: {match['language'] or 'text'}\n\n{body}\n"


def convert_fences(lines: list[str]) -> None:
    """Replace each fenced block in `lines`, in place, with a `.. code-block::` directive."""
    lines[:] = CODE_FENCE.sub(_code_block, "\n".join(lines)).split("\n")


def _docstring(app: Sphinx, what: str, name: str, obj: object, options: object, lines: list[str]) -> None:
    convert_fences(lines)


def _click_description(app: Sphinx, ctx: object, lines: list[str]) -> None:
    convert_fences(lines)


def _connect_click(app: Sphinx, config: Config) -> None:
    # sphinx-click's event exists only if the repo loads it, and every extension is loaded by now
    if "sphinx_click" in app.extensions:
        app.connect("sphinx-click-process-description", _click_description)


def setup(app: Sphinx) -> dict[str, Any]:
    # autodoc defines the event; sphinx-autoapi emits it too
    app.setup_extension("sphinx.ext.autodoc")
    app.connect("autodoc-process-docstring", _docstring, priority=400)  # before Napoleon's 500
    app.connect("config-inited", _connect_click)
    return {"parallel_read_safe": True, "parallel_write_safe": True}

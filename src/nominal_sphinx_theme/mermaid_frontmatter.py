"""Let ```mermaid blocks use Mermaid's own --- front matter.

Mermaid sets per-diagram options in YAML front matter at the top of the diagram:

    ```mermaid
    ---
    config:
      layout: elk
    ---
    flowchart TB
    ```

VS Code's Markdown preview and GitHub read that, but MyST reads a leading --- block as
the directive's options, and sphinxcontrib-mermaid then fails on the YAML `config`
mapping. Before parsing, this rewrites the front matter as the directive options
sphinxcontrib-mermaid expects (`:config:` as JSON, `:title:`), which it turns back into
front matter in the HTML. The source stays plain Mermaid for the previews.

A `name` key becomes the `:name:` option, which is the diagram's HTML id, so a stylesheet
can style one diagram. Mermaid ignores front matter keys it doesn't know.

The theme loads this when a project's extensions include sphinxcontrib.mermaid.
"""

import json
import re
from pathlib import Path

import yaml
from sphinx.application import Sphinx

_FRONT_MATTER = re.compile(
    r"^(?P<fence>`{3,})[ \t]*\{?mermaid\}?[ \t]*\n---[ \t]*\n(?P<yaml>.*?)\n---[ \t]*\n",
    re.MULTILINE | re.DOTALL,
)


def _rewrite(match: re.Match) -> str:
    meta = yaml.safe_load(match["yaml"]) or {}
    options = []
    if "config" in meta:
        options.append(f":config: {json.dumps(meta['config'])}")
    if "title" in meta:
        options.append(f":title: {meta['title']}")
    if "name" in meta:
        options.append(f":name: {meta['name']}")
    return f"{match['fence']}mermaid\n" + "".join(f"{line}\n" for line in options)


def _source_read(app: Sphinx, docname: str, source: list[str]) -> None:
    source[0] = _FRONT_MATTER.sub(_rewrite, source[0])


def _include_read(app: Sphinx, relative_path: Path, parent_docname: str, content: list[str]) -> None:
    # a diagram in an included file, such as a snippet, keeps its front matter too
    content[0] = _FRONT_MATTER.sub(_rewrite, content[0])


def setup(app: Sphinx) -> dict:
    app.connect("source-read", _source_read)
    app.connect("include-read", _include_read)
    return {"parallel_read_safe": True}

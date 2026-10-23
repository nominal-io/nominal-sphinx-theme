"""Shared snippets: MyST fragments in snippets/ that any project using the theme can include.

In a MyST page::

    ```{nominal-snippet} api-keys-setup
    ```

renders snippets/api-keys-setup.md in its place, as if it were written there. A snippet's
images sit beside it and are linked relative to it. They're copied into the project's source
folder, under _nominal_snippets/ (ignored by git), when the build starts, since Sphinx only
resolves images there, and the snippet's image paths are rewritten to point at the copies.
"""

import shutil
from pathlib import Path, PurePosixPath
from typing import Any

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util.docutils import SphinxDirective

SNIPPETS = Path(__file__).parent / "snippets"
# the copies of the snippets' images, in each project's source folder
COPIES = "_nominal_snippets"
IMAGES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}


class NominalSnippet(SphinxDirective):
    required_arguments = 1

    def run(self) -> list[nodes.Node]:
        from myst_parser.mocking import MockState

        if not isinstance(self.state, MockState):
            raise self.error("nominal-snippet works only in MyST pages")
        name = self.arguments[0].removesuffix(".md")
        path = SNIPPETS / f"{name}.md"
        if not path.is_file():
            raise self.error(f"unknown snippet {name!r}")
        self.env.note_dependency(str(path))

        # rendered into the page as MyST's own {include} does, so a snippet's headings become the
        # page's sections; the snippet's images are the ones the page didn't have before
        before = set(map(id, self.state.document.findall(nodes.image)))
        self.state._renderer.nested_render_text(path.read_text(encoding="utf-8"), self.lineno)
        for image in self.state.document.findall(nodes.image):
            uri = image["uri"]
            if id(image) not in before and ":" not in uri and not uri.startswith("/"):
                # a leading / is the project's source folder, to Sphinx
                image["uri"] = f"/{COPIES}/{PurePosixPath(name).parent / uri}"
        return []


def _copy_images(app: Sphinx) -> None:
    # files are written only when changed, so sphinx-autobuild doesn't rebuild on every build
    dest = Path(app.srcdir) / COPIES
    for src in SNIPPETS.rglob("*"):
        if src.suffix.lower() in IMAGES:
            copy = dest / src.relative_to(SNIPPETS)
            if not copy.exists() or copy.read_bytes() != src.read_bytes():
                copy.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, copy)
    ignore = dest / ".gitignore"
    if dest.exists() and not ignore.exists():
        ignore.write_text("*\n")


def _exclude_copies(app: Sphinx, config: Config) -> None:
    config.exclude_patterns.append(f"{COPIES}/**")


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_directive("nominal-snippet", NominalSnippet)
    app.connect("config-inited", _exclude_copies)
    app.connect("builder-inited", _copy_images)
    return {"parallel_read_safe": True, "parallel_write_safe": True}

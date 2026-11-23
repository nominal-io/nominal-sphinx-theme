"""The ``example-gallery`` directive: a card grid for the notebooks beside the page.

A notebook is a MyST Markdown file with ``kernelspec`` in its front matter. Its card shows the first
``#`` heading as the title, over an image. The image is, in order of preference:

1. the front matter's ``thumbnail`` key, a path relative to the notebook; ``thumbnail: false`` shows no image;
2. the first image output of a cell tagged ``thumbnail``;
3. the notebook's last image output, such as its last plot.

A notebook without an image, such as one that wasn't executed, gets a tile with the front matter's
``icon`` as an octicon (with ``sphinx_design`` loaded), or an empty tile. The notebooks are listed in
the sidebar by the root page's toctree, not here.
"""

from pathlib import Path
from typing import Any

import yaml
from docutils import nodes
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective
from sphinx.util.osutil import relative_uri

logger = logging.getLogger(__name__)
STATIC_PATH = Path(__file__).parent / "static"
THUMBNAIL_TAG = "tag_thumbnail"


class example_card(nodes.General, nodes.Element):
    """One card: the page it links to and its title, with the icon, if any, as its children."""


class example_gallery(nodes.General, nodes.Element):
    """Where the cards go; replaced once every page's thumbnail is known."""


def _notebook_card(path: Path) -> tuple[str, str] | None:
    """(title, icon) for a MyST notebook, or None for any other page."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    front, _, body = text[4:].partition("\n---\n")
    meta = yaml.safe_load(front) or {}
    if "kernelspec" not in meta:
        return None
    title = next((line[2:].strip() for line in body.splitlines() if line.startswith("# ")), path.stem)
    return title, str(meta.get("icon") or "")


class ExampleGallery(SphinxDirective):
    def run(self) -> list[nodes.Node]:
        folder = Path(self.env.doc2path(self.env.docname)).parent
        prefix = self.env.docname.rpartition("/")[0]
        octicons = "sphinx_design" in self.config.extensions
        gallery = example_gallery()
        refs = set()
        for path in sorted(folder.glob("*.md")):
            card = _notebook_card(path)
            if card is None:
                continue
            self.env.note_dependency(path)
            title, icon = card
            ref = f"{prefix}/{path.stem}" if prefix else path.stem
            refs.add(ref)
            node = example_card(ref=ref, title=title)
            if icon and octicons:
                node += self.state.inline_text(f"{{octicon}}`{icon}`", self.lineno)[0]
            gallery += node
        self.env.example_galleries[self.env.docname] = refs
        return [gallery]


def _image_key(env: BuildEnvironment, node: nodes.image) -> str | None:
    candidate = node.get("candidates", {}).get("*")
    return candidate if candidate in env.images else None


def _output_images(env: BuildEnvironment, root: nodes.Element) -> list[str]:
    """The images in cell outputs under ``root``, in page order."""
    return [
        key
        for output in root.findall(lambda n: isinstance(n, nodes.container) and "cell_output" in n["classes"])
        for node in output.findall(nodes.image)
        if (key := _image_key(env, node))
    ]


def _find_thumbnail(app: Sphinx, doctree: nodes.document) -> None:
    env = app.env
    docname = env.docname
    thumbnail = env.metadata.get(docname, {}).get("thumbnail")
    # Sphinx's metadata holds front matter values as strings: false is "False"
    if thumbnail is False or str(thumbnail).lower() == "false":
        return
    if thumbnail:
        relpath, abspath = env.relfn2path(str(thumbnail), docname)
        if Path(abspath).is_file():
            env.images.add_file(docname, relpath)  # so the builder copies it
            env.note_dependency(abspath, docname=docname)
            env.example_thumbs[docname] = relpath
            return
        logger.warning("thumbnail %r not found", thumbnail, location=docname)

    tagged = [
        key
        for cell in doctree.findall(lambda n: isinstance(n, nodes.container) and THUMBNAIL_TAG in n["classes"])
        for key in _output_images(env, cell)
    ]
    images = _output_images(env, doctree)
    if tagged or images:
        env.example_thumbs[docname] = tagged[0] if tagged else images[-1]


def _image_uri(app: Sphinx, docname: str, key: str) -> str:
    """The copied image's URI relative to the page."""
    destination = app.env.images[key][1]
    return relative_uri(app.builder.get_target_uri(docname), f"{app.builder.imagedir}/{destination}")


def _draw(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    env = app.env
    for gallery in list(doctree.findall(example_gallery)):
        if app.builder.format != "html":
            gallery.parent.remove(gallery)
            continue
        grid = nodes.container(classes=["nominal-gallery"])
        for card in gallery.findall(example_card):
            link = nodes.reference("", "", internal=True, refuri=app.builder.get_relative_uri(docname, card["ref"]))
            key = env.example_thumbs.get(card["ref"])
            if key:
                # raw, to lazy-load the image; the builder copies it, as the page it came from uses it
                src = _image_uri(app, docname, key)
                frame = nodes.inline("", "", nodes.raw("", f'<img src="{src}" alt="" loading="lazy">', format="html"))
                frame["classes"] = ["nominal-gallery-image"]
            else:
                frame = nodes.inline("", "", *card.children, classes=["nominal-gallery-image", "nominal-gallery-empty"])
            link += frame
            link += nodes.inline(card["title"], card["title"], classes=["nominal-gallery-title"])
            grid += nodes.paragraph("", "", link, classes=["nominal-gallery-card"])
        gallery.replace_self(grid)


def _init_env(app: Sphinx) -> None:
    for attr in ("example_galleries", "example_thumbs"):
        if not hasattr(app.env, attr):
            setattr(app.env, attr, {})


def _purge(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    env.example_galleries.pop(docname, None)
    env.example_thumbs.pop(docname, None)


def _merge(app: Sphinx, env: BuildEnvironment, docnames: set[str], other: BuildEnvironment) -> None:
    for docname in docnames:
        if docname in other.example_galleries:
            env.example_galleries[docname] = other.example_galleries[docname]
        if docname in other.example_thumbs:
            env.example_thumbs[docname] = other.example_thumbs[docname]


def _outdated(app: Sphinx, env: BuildEnvironment, added: set[str], changed: set[str], removed: set[str]) -> list[str]:
    """Rebuild a gallery when a page it links to changes (its thumbnail may), or one is added or removed."""
    touched = added | changed | removed
    folders = {docname.rpartition("/")[0] for docname in added | removed}
    return [
        doc
        for doc, refs in env.example_galleries.items()
        if refs & touched or doc.rpartition("/")[0] in folders
    ]


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_node(example_gallery)
    app.add_node(example_card)
    app.add_directive("example-gallery", ExampleGallery)
    app.connect("builder-inited", _init_env)
    # after Sphinx's image collector (500) has registered the page's images
    app.connect("doctree-read", _find_thumbnail, priority=600)
    app.connect("doctree-resolved", _draw)
    app.connect("env-purge-doc", _purge)
    app.connect("env-merge-info", _merge)
    app.connect("env-get-outdated", _outdated)
    return {"parallel_read_safe": True, "parallel_write_safe": True, "env_version": 1}

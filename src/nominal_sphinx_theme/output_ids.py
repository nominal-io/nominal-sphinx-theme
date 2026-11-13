"""Replace the UUIDs in executed notebook outputs with stand-ins, so pages don't publish real IDs.

Example notebooks that run on build create resources in a real workspace, and their outputs show
those resources' IDs: printed RIDs, links into the Nominal app, and the Nominal Python Client's
cards with their copy buttons. Before a page is written, each UUID in a cell's output becomes a
stand-in derived from a hash of it: the same everywhere it appears and across builds, and not
reversible. The code cells shown on the page, and the notebooks people run themselves, keep their
real values.

The default depends on the environment, so a build that publishes fails safe: UUIDs are replaced when
the ``CI`` environment variable is set (as GitHub Actions does), and kept in a local build, so the links
and copy buttons on a locally built page still point at the real resources. Set
``nominal_scramble_output_ids`` in ``conf.py`` to override it. A site built without ``CI`` holds real IDs
and must not be deployed.
"""

import hashlib
import os
import re
from typing import Any

from docutils import nodes
from sphinx.application import Sphinx

# a UUID in a resource ID or URL, such as ri.scout.<instance>.run.<uuid>
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.IGNORECASE)


def _on_ci() -> bool:
    """Whether ``CI`` is set to something other than an empty, ``0`` or ``false`` value."""
    return os.environ.get("CI", "").strip().lower() not in ("", "0", "false")


def _stand_in(match: re.Match[str]) -> str:
    digest = hashlib.sha256(match.group().lower().encode()).hexdigest()
    return f"{digest[:8]}-{digest[8:12]}-{digest[12:16]}-{digest[16:20]}-{digest[20:32]}"


def _scramble_output_ids(app: Sphinx, doctree: nodes.document) -> None:
    if not app.config.nominal_scramble_output_ids:
        return
    # myst-nb puts each cell's output in a container with the cell_output class; rich displays are
    # raw HTML in it, so this also covers attributes such as links and copy-button values
    outputs = doctree.findall(
        lambda node: isinstance(node, nodes.container) and "cell_output" in node["classes"]
    )
    for output in list(outputs):
        for text in list(output.findall(nodes.Text)):
            scrambled = UUID.sub(_stand_in, text)
            if scrambled != text:
                text.parent.replace(text, nodes.Text(scrambled))


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_config_value("nominal_scramble_output_ids", _on_ci(), "env", types=[bool])
    app.connect("doctree-read", _scramble_output_ids)
    return {"parallel_read_safe": True, "parallel_write_safe": True}

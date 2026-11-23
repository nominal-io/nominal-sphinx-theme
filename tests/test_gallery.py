import base64
import io
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

# a 1x1 PNG
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)

CONF = """
from docutils import nodes

extensions = ["myst_parser", "sphinx_design", "nominal_sphinx_theme"]
myst_enable_extensions = ["colon_fence"]
html_theme = "shibuya"


# docutils' container directive turns "_" in a class into "-"; myst-nb's cell classes keep it
def restore_classes(app, doctree):
    for node in doctree.findall(nodes.Element):
        node["classes"] = [c.replace("cell-output", "cell_output").replace("tag-thumbnail", "tag_thumbnail") for c in node["classes"]]


def setup(app):
    app.connect("doctree-read", restore_classes, priority=400)
"""

INDEX = """\
# Examples

```{example-gallery}
```

```{toctree}
:hidden:

alpha
beta
```
"""


def notebook(title: str, *, front: str = "", body: str = "") -> str:
    """A MyST notebook, with the front matter keys in ``front``."""
    return f"---\n{front}kernelspec:\n  name: python3\n---\n\n# {title}\n\n{body}"


def output(image: str) -> str:
    """A cell's output with an image, shaped like myst-nb's."""
    return f":::{{container}} cell_output\n![]({image})\n:::\n\n"


def build(tmp_path: Path, pages: dict[str, str], images=("one.png", "two.png", "thumb.png")) -> tuple[str, int, str]:
    """Build a project with warnings as errors: the gallery page's HTML, status and warnings."""
    src = tmp_path / "src"
    src.mkdir(exist_ok=True)
    (src / "conf.py").write_text(CONF)
    (src / "index.md").write_text(INDEX)
    for name in images:
        (src / name).write_bytes(PNG)
    for name, text in pages.items():
        (src / f"{name}.md").write_text(text)
    out = tmp_path / "out"
    warnings = io.StringIO()
    with docutils_namespace():
        app = Sphinx(src, src, out, tmp_path / "doctrees", "dirhtml", status=None, warning=warnings, warningiserror=True)
        app.build()
    return (out / "index.html").read_text(), app.statuscode, warnings.getvalue()


def cards(html: str) -> dict[str, str]:
    """Each card's HTML, by its title."""
    found = {}
    for card in html.split('class="nominal-gallery-card"')[1:]:
        card = card.split("</p>")[0]
        title = card.split('class="nominal-gallery-title">')[1].split("<")[0]
        found[title] = card
    return found


def test_last_image_output_is_the_thumbnail(tmp_path):
    pages = {
        "alpha": notebook("Alpha", body=output("one.png") + output("two.png")),
        "beta": notebook("Beta"),
    }
    html, status, warnings = build(tmp_path, pages)
    assert status == 0, warnings
    alpha = cards(html)["Alpha"]
    assert 'src="_images/two.png"' in alpha
    assert 'loading="lazy"' in alpha
    assert (tmp_path / "out" / "_images" / "two.png").read_bytes() == PNG


def test_tagged_cell_beats_the_last_image(tmp_path):
    tagged = "::::{container} cell tag_thumbnail\n" + output("one.png") + "::::\n\n"
    pages = {
        "alpha": notebook("Alpha", body=tagged + output("two.png")),
        "beta": notebook("Beta"),
    }
    html, status, warnings = build(tmp_path, pages)
    assert status == 0, warnings
    assert 'src="_images/one.png"' in cards(html)["Alpha"]


def test_front_matter_overrides_the_outputs(tmp_path):
    pages = {
        "alpha": notebook("Alpha", front="thumbnail: thumb.png\n", body=output("one.png")),
        "beta": notebook("Beta"),
    }
    html, status, warnings = build(tmp_path, pages)
    assert status == 0, warnings
    alpha = cards(html)["Alpha"]
    assert 'src="_images/thumb.png"' in alpha
    assert "one.png" not in alpha


def test_thumbnail_false_shows_no_image(tmp_path):
    pages = {
        "alpha": notebook("Alpha", front="thumbnail: false\n", body=output("one.png")),
        "beta": notebook("Beta"),
    }
    html, status, warnings = build(tmp_path, pages)
    assert status == 0, warnings
    alpha = cards(html)["Alpha"]
    assert "<img" not in alpha
    assert "nominal-gallery-empty" in alpha


def test_no_image_keeps_the_icon_and_title(tmp_path):
    # a build that didn't run the notebooks has no outputs: no warnings, so -W builds pass
    pages = {
        "alpha": notebook("Alpha", front="icon: pulse\n"),
        "beta": notebook("Beta"),
    }
    html, status, warnings = build(tmp_path, pages)
    assert status == 0, warnings
    found = cards(html)
    assert "nominal-gallery-empty" in found["Alpha"]
    assert "sd-octicon" in found["Alpha"]
    assert "<img" not in found["Alpha"]
    assert "sd-octicon" not in found["Beta"]


def test_images_outside_outputs_and_other_pages_are_ignored(tmp_path):
    pages = {
        "alpha": notebook("Alpha", body="![a logo](one.png)\n"),
        "beta": notebook("Beta"),
        "notes": "---\ntitle: Notes\n---\n\n# Not a notebook\n",
    }
    html, status, warnings = build(tmp_path, pages)
    assert "<img" not in cards(html)["Alpha"]
    assert "Not a notebook" not in "".join(cards(html))

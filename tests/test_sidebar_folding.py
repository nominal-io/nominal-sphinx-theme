import io
import re
from pathlib import Path

import pytest
from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

ROOT = """# Home

```{toctree}
:hidden:
:caption: Get started

start
```

```{toctree}
:hidden:
:caption: Guides & more

guide
other
```
"""

# each sidebar group's caption, whether it's marked open, and whether its list is hidden
GROUP = re.compile(
    r'<p class="caption"[^>]*>(?:<button[^>]*aria-expanded="(\w+)"[^>]*>)?<span class="caption-text">([^<]*)</span>'
    r".*?</p>\s*<ul( hidden)?",
    re.DOTALL,
)


def build(tmp_path: Path, conf: str, root: str = ROOT) -> tuple[Path, int, str]:
    """Build a small project with two sidebar groups: its output folder, status and warnings."""
    src = tmp_path / "src"
    src.mkdir(exist_ok=True)
    (src / "conf.py").write_text(f'extensions = ["myst_parser", "nominal_sphinx_theme"]\nhtml_theme = "shibuya"\n{conf}')
    (src / "index.md").write_text(root)
    for name in ("start", "guide", "other"):
        (src / f"{name}.md").write_text(f"# {name.title()}\n")
    warnings = io.StringIO()
    with docutils_namespace():
        app = Sphinx(src, src, tmp_path / "out", tmp_path / "doctrees", "dirhtml", status=None, warning=warnings, warningiserror=True)
        app.build()
    return tmp_path / "out", app.statuscode, warnings.getvalue()


def groups(out: Path, page: str) -> dict[str, tuple[str | None, bool]]:
    html = (out / page / "index.html").read_text()
    sidebar = html[html.index('class="globaltoc"') :]
    return {name.replace("&amp;", "&"): (expanded or None, bool(hidden)) for expanded, name, hidden in GROUP.findall(sidebar)}


def test_groups_do_not_fold_by_default(tmp_path):
    out, status, warnings = build(tmp_path, "")
    assert status == 0, warnings
    assert groups(out, "start") == {"Get started": (None, False), "Guides & more": (None, False)}
    assert "nominal-fold" not in (out / "start" / "index.html").read_text()


def test_listed_groups_start_open(tmp_path):
    out, status, warnings = build(tmp_path, 'nominal_sidebar_open = ["Get started"]')
    assert status == 0, warnings
    assert groups(out, "start") == {"Get started": ("true", False), "Guides & more": ("false", True)}


def test_current_page_group_starts_open(tmp_path):
    out, status, warnings = build(tmp_path, 'nominal_sidebar_open = ["Get started"]')
    assert status == 0, warnings
    assert groups(out, "guide") == {"Get started": ("true", False), "Guides & more": ("true", False)}


@pytest.mark.parametrize(("setting", "expanded", "hidden"), [("True", "true", False), ("False", "false", True)])
def test_all_groups_open_or_folded(tmp_path, setting, expanded, hidden):
    out, status, warnings = build(tmp_path, f"nominal_sidebar_open = {setting}")
    assert status == 0, warnings
    # the home page is in neither group, so neither opens for being current
    assert groups(out, ".") == {"Get started": (expanded, hidden), "Guides & more": (expanded, hidden)}


def test_unknown_caption_warns(tmp_path):
    _, status, warnings = build(tmp_path, 'nominal_sidebar_open = ["Get Started"]')
    assert status == 1
    assert "nominal_sidebar_open: no toctree caption 'Get Started' in index" in warnings


def test_folds_with_tabs(tmp_path):
    # with tabs, the sidebar keeps only the current tab's groups, then folds them
    (tmp_path / "src" / "ref").mkdir(parents=True)
    (tmp_path / "src" / "ref" / "index.md").write_text("# Reference\n")
    conf = (
        'nominal_sidebar_open = ["Get started"]\n'
        'html_theme_options = {"nav_links": [{"title": "Guides", "url": "index"}, {"title": "Reference", "url": "ref/index"}]}\n'
    )
    out, status, warnings = build(tmp_path, conf, ROOT + "\n```{toctree}\n:hidden:\n:caption: Reference\n\nref/index\n```\n")
    assert status == 0, warnings
    assert groups(out, "start") == {"Get started": ("true", False), "Guides & more": ("false", True)}
    assert groups(out, "ref") == {"Reference": ("true", False)}

"""Nominal's look for Sphinx docs: the Shibuya theme, styled like instro's docs.

In a project's conf.py::

    from nominal_sphinx_theme import theme_options

    extensions = [..., "nominal_sphinx_theme"]
    html_theme = "shibuya"
    html_theme_options = theme_options(
        github_url="https://github.com/nominal-io/instro",
        light_logo="_static/logo/instro-logo-solid-black.svg",  # the project's own logo, if it has one
        dark_logo="_static/logo/instro-logo-solid-white.svg",
    )

The header shows the Nominal logo, linking to the docs landing page (opened at the project's
language, via the hub's /{lang}/ redirect), then the project's logo (or its name). Projects published on their own, outside the docs hub, set
``nominal_hub_url = "https://dev.nominal.io/"`` so the Nominal logo leads there.

Tabs: each ``nav_links`` entry pointing at a page in a folder (``{"title": "Examples", "url":
"examples/index"}``) is a section: pages in that folder belong to it, and every other page to the
tab without a folder (``"index"``). The current tab is underlined, and the left sidebar shows only
its toctree groups, so give each section its own captioned, hidden toctree in the root document.
Set ``nominal_section_sidebar = False`` to keep the full sidebar.
"""

import posixpath
import re
from pathlib import Path
from typing import Any

from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util.osutil import relative_uri

__version__ = "0.1.0"

HERE = Path(__file__).parent

# the landing page's fonts
FONTS = "https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500;700&display=swap"

# the rendered sidebar: one block per captioned toctree group, and the links in it
_CAPTION = re.compile(r'(?=<p class="caption")')
_HREF = re.compile(r'href="([^"#]*)')


def theme_options(*, github_url: str | None = None, **overrides: Any) -> dict[str, Any]:
    """Shibuya options for a Nominal docs site; keyword arguments override the defaults."""
    options: dict[str, Any] = {
        "accent_color": "gray",
        # dark, like the landing page, unless the visitor picks light with the theme switch
        "color_mode": "dark",
        "x_url": "https://x.com/nominal_io",
        "linkedin_url": "https://linkedin.com/company/nominal-io",
        # header icons before the buttons; a project lists its own (Shibuya's nav_socials format)
        "nav_socials": [],
        "toctree_titles_only": True,
    }
    if github_url:
        options["github_url"] = github_url
    options.update(overrides)
    return options


def _on_config_inited(app: Sphinx, config: Config) -> None:
    # appended, so a project's own _static and _templates win over the theme's
    config.html_static_path.append(str(HERE / "static"))
    config.templates_path.append(str(HERE / "templates"))
    if not config.html_favicon:
        config.html_favicon = str(HERE / "static" / "favicon.svg")


def _tabs(app: Sphinx) -> dict[str, str]:
    """Each internal nav_links tab's folder ("" for the tab without one) -> its url."""
    tabs: dict[str, str] = {}
    for link in app.config.html_theme_options.get("nav_links") or []:
        url = link.get("url") or ""
        if url and not re.match(r"[a-z]+:", url) and not link.get("children"):
            folder = posixpath.dirname(url)
            tabs.setdefault(folder + "/" if folder else "", url)
    return tabs


def _section(path: str, folders: list[str]) -> str:
    return max((f for f in folders if f and path.startswith(f)), key=len, default="")


def _on_page(app: Sphinx, pagename: str, templatename: str, context: dict[str, Any], doctree: Any) -> None:
    target = app.builder.get_target_uri(pagename)
    # the docs hub's language folder, one above this project's home at /{lang}/{project}/: it opens
    # the landing page with that language's card (scripts/site.py writes /{lang}/index.html)
    context["nominal_hub_url"] = app.config.nominal_hub_url or relative_uri(target, "") + "../"
    context["nominal_hub_external"] = bool(app.config.nominal_hub_url)

    tabs = _tabs(app)
    current = _section(pagename, list(tabs))
    context["nominal_tab"] = tabs.get(current)
    toctree = context.get("toctree")
    if not app.config.nominal_section_sidebar or len(tabs) < 2 or toctree is None:
        return
    # where this page's relative links start: its folder (dirhtml pages are folders themselves)
    page_dir = target if target.endswith("/") else posixpath.dirname(target) + "/"
    if page_dir == "/":
        page_dir = ""

    def section_toctree(**kwargs: Any) -> str:
        kept = []
        for block in _CAPTION.split(toctree(**kwargs)):
            href = _HREF.search(block)
            if not href:
                continue
            linked = posixpath.normpath(posixpath.join(page_dir, href.group(1) or "."))
            if _section(linked + "/", list(tabs)) == current:
                kept.append(block)
        return "".join(kept)

    context["toctree"] = section_toctree


def _on_builder_inited(app: Sphinx) -> None:
    ga_id = app.config.nominal_ga_id
    if ga_id:
        app.add_js_file(f"https://www.googletagmanager.com/gtag/js?id={ga_id}", loading_method="async")
        app.add_js_file(
            None,
            body=(
                "window.dataLayer = window.dataLayer || [];"
                "function gtag() { dataLayer.push(arguments); }"
                f'gtag("js", new Date()); gtag("config", "{ga_id}");'
            ),
        )


def _api_contents(app: Sphinx, doctree: nodes.document) -> None:
    # Keep all targets and reference content; only omit non-callable objects from the local TOC.
    for node in doctree.findall(addnodes.desc):
        if node.get("domain") == "py" and node.get("objtype") in {"attribute", "property", "data", "type"}:
            node["no-contents-entry"] = True


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_config_value("nominal_ga_id", None, "html", types=[str, type(None)])
    # where the header's Nominal logo leads; None: the docs hub's landing page, relative to the project
    app.add_config_value("nominal_hub_url", None, "html", types=[str, type(None)])
    # show only the current tab's toctree groups in the left sidebar
    app.add_config_value("nominal_section_sidebar", True, "html", types=[bool])
    app.connect("config-inited", _on_config_inited)
    app.connect("builder-inited", _on_builder_inited)
    app.connect("html-page-context", _on_page)
    app.connect("doctree-read", _api_contents, priority=400)
    app.add_css_file(FONTS)
    app.add_css_file("nominal.css")
    app.add_js_file("nominal.js")
    return {"version": __version__, "parallel_read_safe": True, "parallel_write_safe": True}

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

Folding: ``nominal_sidebar_open`` makes each captioned toctree group in the left sidebar fold under
its caption. ``True`` starts every group open, ``False`` every group folded, and a list of captions
(``["Get started"]``) starts those open. The group holding the current page always starts open.
The default, ``None``, leaves the groups unfolded, with plain captions.
"""

import html
import posixpath
import re
from pathlib import Path
from typing import Any

from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.environment import BuildEnvironment
from sphinx.util import logging
from sphinx.util.osutil import relative_uri

__version__ = "0.1.0"

HERE = Path(__file__).parent
logger = logging.getLogger(__name__)

# the landing page's fonts
FONTS = "https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500;700&display=swap"

# the rendered sidebar: one block per captioned toctree group, and the links in it
_CAPTION = re.compile(r'(?=<p class="caption")')
_HREF = re.compile(r'href="([^"#]*)')
# a group's caption, and an entry marked as the current page (or one of its ancestors)
_CAPTION_TEXT = re.compile(r'(<p class="caption"[^>]*>)(.*?)(</p>)', re.DOTALL)
_CURRENT = re.compile(r'class="[^"]*\bcurrent\b')
_TAG = re.compile(r"<[^>]+>")


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
    sectioned = app.config.nominal_section_sidebar and len(tabs) >= 2
    open_groups = app.config.nominal_sidebar_open
    if toctree is None or not (sectioned or open_groups is not None):
        return
    # where this page's relative links start: its folder (dirhtml pages are folders themselves)
    page_dir = target if target.endswith("/") else posixpath.dirname(target) + "/"
    if page_dir == "/":
        page_dir = ""

    def sidebar_toctree(**kwargs: Any) -> str:
        kept = []
        for block in _CAPTION.split(toctree(**kwargs)):
            if sectioned:
                href = _HREF.search(block)
                if not href:
                    continue
                linked = posixpath.normpath(posixpath.join(page_dir, href.group(1) or "."))
                if _section(linked + "/", list(tabs)) != current:
                    continue
            kept.append(block if open_groups is None else _fold(block, open_groups))
        return "".join(kept)

    context["toctree"] = sidebar_toctree


def _caption_name(caption_html: str) -> str:
    return html.unescape(_TAG.sub("", caption_html)).strip()


def _fold(block: str, open_groups: bool | list[str]) -> str:
    """A sidebar group whose caption is a button that folds it (nominal.js), open or folded to start."""
    caption = _CAPTION_TEXT.match(block)
    if not caption:
        return block
    start, inner, end = caption.groups()
    group = block[caption.end() :]
    is_open = (
        open_groups is True
        or (isinstance(open_groups, list) and _caption_name(inner) in open_groups)
        or bool(_CURRENT.search(group))
    )
    if not is_open:
        group = group.replace("<ul", "<ul hidden", 1)
    button = (
        f'<button type="button" class="nominal-fold" aria-expanded="{str(is_open).lower()}">'
        f'{inner}<i class="i-lucide chevron-right"></i></button>'
    )
    return start + button + end + group


def _check_open_groups(app: Sphinx, env: BuildEnvironment) -> None:
    # a renamed caption would otherwise leave its group folded without a word
    open_groups = app.config.nominal_sidebar_open
    if not isinstance(open_groups, list):
        return
    captions = {node.get("caption") for node in env.get_doctree(app.config.root_doc).findall(addnodes.toctree)}
    for name in open_groups:
        if name not in captions:
            logger.warning("nominal_sidebar_open: no toctree caption %r in %s", name, app.config.root_doc)


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


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_config_value("nominal_ga_id", None, "html", types=[str, type(None)])
    # where the header's Nominal logo leads; None: the docs hub's landing page, relative to the project
    app.add_config_value("nominal_hub_url", None, "html", types=[str, type(None)])
    # show only the current tab's toctree groups in the left sidebar
    app.add_config_value("nominal_section_sidebar", True, "html", types=[bool])
    # fold the left sidebar's toctree groups: True/False start them all open/folded, a list of
    # captions starts those open; None (the default) doesn't fold them
    app.add_config_value("nominal_sidebar_open", None, "html", types=[type(None), bool, list])
    # the {nominal-snippet} directive: fragments shared by every project using the theme
    app.setup_extension("nominal_sphinx_theme.snippet_directive")
    app.connect("config-inited", _on_config_inited)
    app.connect("builder-inited", _on_builder_inited)
    app.connect("html-page-context", _on_page)
    app.connect("env-check-consistency", _check_open_groups)
    app.add_css_file(FONTS)
    app.add_css_file("nominal.css")
    app.add_js_file("nominal.js")
    return {"version": __version__, "parallel_read_safe": True, "parallel_write_safe": True}

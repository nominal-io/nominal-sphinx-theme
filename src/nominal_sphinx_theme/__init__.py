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

The header shows the Nominal logo, reading NOMINAL / DOCS / DEVELOPERS, then the project's logo (or its
name). NOMINAL links to nominal.io, and DOCS and DEVELOPERS to the docs hub's home page (its For
developers tab). Projects published on their own, outside the docs hub, set
``nominal_hub_url = "https://dev.nominal.io/"`` so those words lead there.

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

from docutils import nodes
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

# API field lists whose entries are "name (type) -- description", and that separator, before or
# after smart quotes turn it into an en dash
_PARAM_FIELDS = {"parameters", "keyword arguments", "other parameters"}
_PARAM_SEPARATOR = re.compile(r" (?:--|–) ")

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
    # the docs hub's home page, two above this project's home at /{lang}/{project}/
    context["nominal_hub_url"] = app.config.nominal_hub_url or relative_uri(target, "") + "../../"

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


def _split_param(para: nodes.paragraph) -> None:
    """Split "name (type) -- description" into a head paragraph and a description paragraph after it."""
    for index, child in enumerate(para.children):
        if not isinstance(child, nodes.Text):
            continue
        match = _PARAM_SEPARATOR.search(child)
        if not match:
            continue
        before, after = str(child)[: match.start()], str(child)[match.end() :]
        desc = nodes.paragraph(classes=["nominal-param-desc"])
        if after:
            desc += nodes.Text(after)
        desc.extend(para.children[index + 1 :])
        del para.children[index:]
        if before:
            para += nodes.Text(before)
        para["classes"].append("nominal-param-head")
        para.parent.insert(para.parent.index(para) + 1, desc)
        return


def _split_params(app: Sphinx, doctree: nodes.document) -> None:
    # each parameter's name and type on a line of its own, its description below (nominal.css)
    for field in list(doctree.findall(nodes.field)):
        if field[0].astext().strip().rstrip(":").lower() not in _PARAM_FIELDS:
            continue
        body = field[1]
        if body.children and isinstance(body[0], nodes.bullet_list):
            body[0]["classes"].append("nominal-params")
            heads = [item[0] for item in body[0].children if item.children and isinstance(item[0], nodes.paragraph)]
        else:
            heads = [body[0]] if body.children and isinstance(body[0], nodes.paragraph) else []
        for para in heads:
            _split_param(para)


def _set_highlighting(app: Sphinx) -> None:
    # Shibuya's highlighter writes a light and a dark style; swap in ours, unless the project picked
    # its own pygments_style (Shibuya then uses that one alone)
    highlighter = getattr(app.builder, "highlighter", None)
    if app.config.pygments_style is not None or not hasattr(highlighter, "dark_style_name"):
        return
    new = type(highlighter)("html", app.config.nominal_pygments_style)
    new.dark_style_name = app.config.nominal_pygments_dark_style
    app.builder.highlighter = new


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_config_value("nominal_ga_id", None, "html", types=[str, type(None)])
    # code highlighting in light and dark mode: Pygments style names, or dotted paths to style classes
    # (default: Atom's One Light and One Dark, in pygments_styles.py)
    styles = "nominal_sphinx_theme.pygments_styles"
    app.add_config_value("nominal_pygments_style", f"{styles}.OneLightStyle", "html", types=[str])
    app.add_config_value("nominal_pygments_dark_style", f"{styles}.OneDarkStyle", "html", types=[str])
    # where DOCS and DEVELOPERS in the header's logo lead; None: the docs hub's home page, relative to the project
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
    # after Shibuya's builder-inited, which sets up its highlighter
    app.connect("builder-inited", _set_highlighting, priority=900)
    app.connect("doctree-read", _split_params)
    app.connect("html-page-context", _on_page)
    app.connect("env-check-consistency", _check_open_groups)
    app.add_css_file(FONTS)
    app.add_css_file("nominal.css")
    app.add_css_file("nominal-path.css")
    app.add_js_file("nominal.js")
    return {"version": __version__, "parallel_read_safe": True, "parallel_write_safe": True}

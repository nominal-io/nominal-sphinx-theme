# nominal-sphinx-theme

Nominal's look for Sphinx docs, based on the [Shibuya](https://shibuya.lepture.com/) theme 
## Install

```sh
uv add "nominal-sphinx-theme @ git+https://github.com/nominal-io/nominal-sphinx-theme"
# or: pip install git+https://github.com/nominal-io/nominal-sphinx-theme
```

## Use

In `conf.py`:

```python
from nominal_sphinx_theme import theme_options

extensions = [..., "nominal_sphinx_theme"]
html_theme = "shibuya"
html_theme_options = theme_options(
    github_url="https://github.com/nominal-io/<repo>",
    # optional: the project's own logo, shown after the Nominal logo
    light_logo="_static/logo/<project>-black.svg",
    dark_logo="_static/logo/<project>-white.svg",
    # optional: header tabs; each link's folder is a section
    nav_links=[
        {"title": "Guides", "url": "index"},
        {"title": "Examples", "url": "examples/index"},
    ],
)
```

Any other keyword to `theme_options` is passed through as a Shibuya option.

## Config

| Setting                   | Default | Effect                                                                 |
| ------------------------- | ------- | ---------------------------------------------------------------------- |
| `nominal_hub_url`         | `None`  | Where the Nominal logo links. `None` = the docs hub, one level up. Set to `"https://dev.nominal.io/"` for standalone sites. |
| `nominal_section_sidebar` | `True`  | Sidebar shows only the current tab's captioned toctrees.               |
| `nominal_ga_id`           | `None`  | Google Analytics measurement ID.                                       |

A project's own `_static` and `_templates` override the theme's files of the same name.

## Header

The header shows the Nominal logo, then `/` and the project's logo (or its name, without one).
The Nominal logo links to the developer docs hub's landing page, with the project's language card
open. The link is relative (the `/{lang}/` folder above a project's home at `/{lang}/{project}/`),
so it works on the hub and in its offline copies. A site published on its own, outside the hub,
sets `nominal_hub_url` instead.

## Tabs

Each `nav_links` entry that points at a page in a folder, e.g.
`{"title": "Examples", "url": "examples/index"}`, is a tab for the pages in that folder; every other
page belongs to the tab without a folder (`"index"`). The current tab is underlined, and the left
sidebar shows only its toctree groups (unless `nominal_section_sidebar = False`). So with tabs,
give each section its own captioned, `:hidden:` toctree in the root document.

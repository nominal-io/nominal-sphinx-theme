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
| `nominal_hub_url`         | `None`  | The docs hub's home page, where DOCS in the logo links (and DEVELOPERS, to its `developers/`). `None` = the docs hub's home page, two levels up. Set to `"https://dev.nominal.io/"` for standalone sites. |
| `nominal_section_sidebar` | `True`  | Sidebar shows only the current tab's captioned toctrees.               |
| `nominal_sidebar_open`    | `None`  | Sidebar groups fold under their captions. See [Folding sidebar groups](#folding-sidebar-groups). |
| `nominal_ga_id`           | `None`  | Google Analytics measurement ID.                                       |

A project's own `_static` and `_templates` override the theme's files of the same name.

## Header

The header shows the Nominal logo, which reads like a path, NOMINAL / DOCS / DEVELOPERS, then `/` and
the project's logo (or its name, without one). NOMINAL links to nominal.io, DOCS to the docs hub's
home page, and DEVELOPERS to the hub's For developers tab, `developers/`. Those links are relative (the
hub's root, two above a project's home at `/{lang}/{project}/`), so they work on the hub and in its
offline copies. A site published on its own, outside the hub, sets `nominal_hub_url` instead.

On wide screens with tabs, the search sits at the right of the tabs' row, under the buttons.

A tab (`nav_links`) to another site that sets `"external": True` opens in a new tab.

## Social links

The header's right side shows the "Product Guides", "Request a demo" and "Open app" buttons. To put icons before
them, pass `nav_socials` (Shibuya's format): a name such as `"github"` or `"discord"` uses the
matching `<name>_url` option, and a `{"name", "url", "icon"}` dict adds any other link, with any
[Iconify](https://icon-sets.iconify.design/) icon. The default is none.

```python
html_theme_options = theme_options(
    github_url="https://github.com/nominal-io/<repo>",
    discord_url="https://discord.gg/<invite>",
    nav_socials=[
        "github",
        "discord",
        {"name": "Forum", "url": "https://community.example.com", "icon": "lucide:messages-square"},
    ],
)
```

The footer's icons are Shibuya's `foot_socials`: by default, every `<name>_url` that is set (here
GitHub, Discord, and the X and LinkedIn links `theme_options` sets).

## Tabs

Each `nav_links` entry that points at a page in a folder, e.g.
`{"title": "Examples", "url": "examples/index"}`, is a tab for the pages in that folder; every other
page belongs to the tab without a folder (`"index"`). The current tab is underlined, and the left
sidebar shows only its toctree groups (unless `nominal_section_sidebar = False`). So with tabs,
give each section its own captioned, `:hidden:` toctree in the root document.

With tabs, the header has two rows on wide screens: the logos, search and buttons on the first,
and the tabs on the second. On narrow screens the tabs fold into the menu, as before.

A tab can show an icon before its title: give it an `icon` with any
[Iconify](https://icon-sets.iconify.design/) name, as in `nav_socials`.

```python
nav_links=[
    {"title": "Guides", "url": "index", "icon": "lucide:book-open"},
    {"title": "Examples", "url": "examples/index", "icon": "lucide:code"},
]
```

## Folding sidebar groups

Set `nominal_sidebar_open` to make each captioned toctree group in the left sidebar fold under its
caption. Clicking a caption opens or closes its group, and the caption keeps its font.

```python
nominal_sidebar_open = None             # default: groups don't fold
nominal_sidebar_open = True             # every group starts open
nominal_sidebar_open = False            # every group starts folded
nominal_sidebar_open = ["Get started"]  # these groups start open, the others folded
```

The group holding the current page always starts open. Captions in the list match the toctrees'
`:caption:` text in the root document, and one that matches none is a build warning.

## Heading links

Clicking the `#` after a heading copies a link to that section, as well as going to it, and
"Copied" shows beside it for a moment. Copying needs a secure page (https, or localhost when
previewing); elsewhere the `#` is a plain link.

## Shared snippets

Snippets are MyST fragments in `src/nominal_sphinx_theme/snippets/` that any project using the theme can include, for content many projects repeat. A MyST page
includes one by its path, without `.md`:

````md
```{nominal-snippet} api-keys-setup
```
````

The snippet renders in its place as if written there, and its headings become the page's
sections. A misspelled name fails the build.

A snippet's images sit beside it, linked relative to it (`![The API keys page](api-keys.png)`,
or a `{figure}`). When a build starts, they're copied into the project's source folder under
`_nominal_snippets/`, which ignores itself in git and is excluded as a source of pages.

Snippets are built in every project that includes them, so a snippet uses only what all of them
have:

- Links to other pages are absolute URLs to the docs hub, not relative links.
- No labels such as `(name)=`. A page that includes two snippets defining one would fail.
- Core MyST, `colon_fence`, and directives every project loads. Not a project's own roles, such as
  pub-docs' `{gloss}`.
- Images as Markdown images or `{image}`/`{figure}`, not HTML `<img>`.
- Tabs use the shared sync groups, `os` and `code`.

A snippet change reaches a project when it updates its theme pin, like any theme change.

| Snippet          | What it covers                                                              |
| ---------------- | --------------------------------------------------------------------------- |
| `api-keys-setup` | The config file, the three values from the **API keys** page, and the CLIs. Needs `sphinx_design` and MyST's `attrs_block`. |

The theme styles callouts for any project: a screenshot with class `callout-screenshot` beside a
`{.callouts}` numbered list gets red numbers matching the screenshot's.

To test the directive:

```sh
uv run --group dev pytest
```

## Docs skill for AI agents

[`skills/nominal-docs/`](skills/nominal-docs/) holds Nominal's shared rules for writing docs and docstrings, as a Claude Code plugin.

To use it in a repo, add this to the repo's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "nominal": { "source": { "source": "github", "repo": "nominal-io/nominal-sphinx-theme" } }
  },
  "enabledPlugins": { "nominal-docs@nominal": true }
}
```

- Repo-specific details (docs folders, build commands, layout) go in that repo's own docs skill or `AGENTS.md`.
- The Style section and the docstring files are written by people. Change them through a PR here.

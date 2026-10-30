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
| `nominal_hub_url`         | `None`  | The docs hub's home page, where DEVELOPERS in the logo links. `None` = the docs hub's home page, one level up. Set to `"https://dev.nominal.io/"` for standalone sites. |
| `nominal_docs_url`        | `"https://dev.nominal.io/"`  | Where DOCS in the logo links, in a new tab.               |
| `nominal_section_sidebar` | `True`  | Sidebar shows only the current tab's captioned toctrees.               |
| `nominal_sidebar_open`    | `None`  | Sidebar groups fold under their captions. See [Folding sidebar groups](#folding-sidebar-groups). |
| `nominal_ga_id`           | `None`  | Google Analytics measurement ID.                                       |

A project's own `_static` and `_templates` override the theme's files of the same name.

## Header

The header shows the Nominal logo, which reads like a path, NOMINAL / DOCS / DEVELOPERS, then `/` and
the project's logo (or its name, without one). NOMINAL links to nominal.io, DOCS to Nominal's docs
(`nominal_docs_url`) in a new tab, and DEVELOPERS to the docs hub's home page. That link is relative
(the hub's root, one above a project's home at `/{project}/`), so it works on the hub and in its
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

## Footer

Below the copyright and icons, the footer shows the theme commit that built the page, abbreviated and
linked to it on GitHub. The full commit is in the stamp's `data-commit` attribute
(`<p class="nominal-theme-commit" data-commit="<sha>">`), for scripts. It's the commit a git install of
the theme recorded, or a local checkout's `HEAD`. Without either, the footer has no stamp.

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

## CI

| Workflow | Runs | Does |
| --- | --- | --- |
| [`tests.yml`](.github/workflows/tests.yml) | PRs and pushes to `main` | The tests in `tests/`, on Python 3.12 and 3.13 |
| [`bump-theme.yml`](.github/workflows/bump-theme.yml) | Called by each repo that uses the theme | Moves that repo's `uv.lock` to the theme's newest commit, in one PR |
| [`docs-gate.yml`](.github/workflows/docs-gate.yml) | Called by each repo's docs workflow | The check that stops a bump PR merging when the docs don't build |
| [`bump-all.yml`](.github/workflows/bump-all.yml) | By hand | Runs every repo's bump now |

### Theme updates

Each repo using the theme pins a commit of it in `uv.lock`. A daily workflow there, calling
`bump-theme.yml`, runs `uv lock --upgrade-package nominal-sphinx-theme`. If that changes `uv.lock`,
NomBot opens one PR, `chore(deps): bump nominal-sphinx-theme to <sha>`, from the branch
`chore/bump-nominal-sphinx-theme`, or updates the one already open. The PR merges itself once the
repo's required checks pass.

- **NomBot:** the workflow mints a NomBot App token. A PR opened with `GITHUB_TOKEN` wouldn't run the
  repo's other workflows, so its docs wouldn't be checked.
- **Auto-merge:** turned on only when the default branch has required checks. With none,
  `gh pr merge --auto` would merge the PR at once, so the workflow leaves it for a person instead.
- **uv:** the bump locks with the newest uv, unless the caller passes `uv-version`. A new uv can move
  `uv.lock` to a new revision, a one-line change.

To bump a repo now, open its **Actions** tab, pick **Bump nominal-sphinx-theme** and click **Run
workflow**. To bump every repo, do the same here with **Bump the theme in every repo**. It runs
`bump-theme.yml`, with a NomBot token that has `actions:write`, in each repo whose docs
dev.nominal.io publishes, read from its
[`sites.toml`](https://github.com/nominal-io/dev.nominal.io/blob/main/sites.toml) on each run, and
in the repos in `EXTRA_REPOS`, which use the theme outside the hub. Its trigger on push to `main`
is there, commented out.

### Docs gate

A bump PR shouldn't merge if the docs don't build, but requiring the docs build on `main` would
block every PR whenever the docs break. So each repo requires `docs-gate / gate` instead. On a bump
PR, the gate fails unless the docs build succeeded. On any other PR, it passes, whatever the docs
build did.

The gate is a job in the same workflow as the docs build, since it needs that job's result. If the
docs workflow runs only for some paths, the gate doesn't run on other PRs, and a required check that
doesn't run blocks the PR. Drop the path filter from `pull_request` first.

### Adding a repo

1. Copy this to `.github/workflows/bump-theme.yml`:

   ```yaml
   name: Bump nominal-sphinx-theme

   on:
     schedule:
       - cron: "0 6 * * *" # daily, 06:00 UTC
     workflow_dispatch:

   permissions:
     contents: read

   jobs:
     bump:
       uses: nominal-io/nominal-sphinx-theme/.github/workflows/bump-theme.yml@<commit> # main, <date>
       # with:
       #   uv-version: "0.13.x"  # lock with this uv instead of the newest
       #   auto-merge: false     # leave every PR for a person
       secrets:
         NOMBOT_APP_ID: ${{ secrets.NOMBOT_APP_ID }}
         NOMBOT_PRIVATE_KEY: ${{ secrets.NOMBOT_PRIVATE_KEY }}
   ```

2. Add the gate to the workflow that builds the docs on PRs, naming its docs job in `needs` and
   `docs-result`:

   ```yaml
     docs-gate:
       needs: build-docs
       if: always()
       uses: nominal-io/nominal-sphinx-theme/.github/workflows/docs-gate.yml@<commit> # main, <date>
       with:
         docs-result: ${{ needs.build-docs.result }}
   ```

3. In the repo's settings, turn on **Allow auto-merge**. Under **Rules → Rulesets**, require the
   status check `docs-gate / gate` on the default branch.
4. Check that the NomBot App is installed there and that the `NOMBOT_APP_ID` and
   `NOMBOT_PRIVATE_KEY` org secrets reach the repo.
5. If dev.nominal.io doesn't publish the repo's docs, add it to `EXTRA_REPOS` in `bump-all.yml`.
   A repo in the hub's `sites.toml` is already included.

- **Pins:** pin `uses:` to a commit of this repo, as for any action. This repo has no releases, so
  the comment is `# main, <date>`, and Dependabot can't move it. When `bump-theme.yml` or
  `docs-gate.yml` changes here, move each repo's pin by hand. The bump itself always takes the
  theme's newest commit.
- **Secrets:** pass the two NomBot secrets, not `secrets: inherit`, which hands every secret in the
  repo to this repo's workflow. Semgrep blocks `secrets: inherit`.
- **Permissions:** a called workflow can't have more `GITHUB_TOKEN` permissions than its caller.
  `bump-theme.yml` asks for `contents: read`, and `docs-gate.yml` for none.

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

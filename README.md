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

## What goes in the theme

The theme holds what every repo using it shares, so a repo gets a change by bumping its pin:

- the look: the header, logo, palette, fonts, code highlighting and API page styling
- fixes to Shibuya and to the extensions repos share, such as MyST, sphinx-design and
  sphinxcontrib-mermaid
- directives more than one repo uses, such as `{nominal-snippet}`
- default Sphinx and MyST settings, which a repo's `conf.py` can override

A repo keeps what only its own docs need: its pages, its logo, and styles and extensions for one
page or project. What exists only because of the docs hub, such as its landing page and the links
between its projects, stays in [dev.nominal.io](https://github.com/nominal-io/dev.nominal.io)
(its README, "Theme or hub"). The theme knows the hub only by its URLs, `nominal_hub_url` and
`nominal_docs_url`.

When a second repo needs something one repo has, move it here rather than copy it. Don't override
the theme's templates or restyle its header in a repo; change them here.

## Config

| Setting                   | Default | Effect                                                                 |
| ------------------------- | ------- | ---------------------------------------------------------------------- |
| `nominal_hub_url`         | `None`  | The docs hub's home page, where DEVELOPERS in the logo links. `None` = the docs hub's home page, one level up. Set to `"https://dev.nominal.io/"` for standalone sites. |
| `nominal_docs_url`        | `"https://dev.nominal.io/"`  | Where DOCS in the logo links, in a new tab.               |
| `nominal_hub_depth`       | `1`     | How many folders the hub's home page is above the project's home, when `nominal_hub_url` is `None`. `0` for the hub's own home page. |
| `nominal_header_project`  | `True`  | The project's logo or name after the Nominal logo. |
| `nominal_header_search`   | `True`  | The search box in the header. |
| `nominal_header_buttons`  | `["product-guides", "request-demo", "open-app"]` | The header's buttons to show. |
| `nominal_section_sidebar` | `True`  | Sidebar shows only the current tab's captioned toctrees.               |
| `nominal_sidebar_open`    | `None`  | Sidebar groups fold under their captions. See [Folding sidebar groups](#folding-sidebar-groups). |
| `nominal_ga_id`           | `"G-6KQ94CEW2M"` | Google Analytics measurement ID, dev.nominal.io's by default. `None` turns analytics off. |
| `nominal_scramble_output_ids` | `True` | Each UUID in an executed notebook's outputs becomes a stand-in derived from a hash of it, so pages don't publish the IDs of resources the build created. Code cells keep their values. |

A project's own `_static` and `_templates` override the theme's files of the same name.

### Defaults

The theme sets these Sphinx and MyST settings, which every repo using it had in its `conf.py`. A
setting in `conf.py`, or on the command line with `-D`, wins. The MyST ones apply only with
`myst_parser` in `extensions`.

| Setting | Default |
| --- | --- |
| `html_title` | `project` |
| `html_copy_source` | `False` |
| `myst_enable_extensions` | `["colon_fence", "deflist", "attrs_inline", "attrs_block", "fieldlist"]` |
| `myst_fence_as_directive` | `["mermaid"]`: a ```` ```mermaid ```` fence is a diagram |
| `myst_heading_anchors` | `6` |
| `myst_links_external_new_tab` | `True`: Markdown links to other sites open in a new tab |
| `mermaid_height` | `"auto"`: each diagram is as tall as its content |
| `codeautolink_concat_default` | `True`: a page's code blocks run in order, so a name imported in one links in later ones |
| `suppress_warnings` | `["codeautolink.parse_block"]`: a Python block that doesn't parse, such as a signature with types, stays unlinked instead of warning |

`html_theme = "shibuya"` and the `extensions` list stay in `conf.py`.

## Header

The header shows the Nominal logo, which reads like a path, NOMINAL / DEV / DEVELOPERS, then `/` and
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

## GitHub tab

With `github_url` and tabs (`nav_links`), a GitHub tab to the repo ends the tabs. Pass
`github_tab=False` to `theme_options` to leave it out. A tab the project already has to the same URL
isn't repeated, and a project without `github_url` or without tabs gets none.

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

## Folding code blocks

Each code block's bar has a "Fold" button at its upper left, the language in the middle, and the copy button at the right. A folded block is only its bar,
so its code can still be copied, and the button reads "Show" until it shows the code again. A "Fold
all code" button above "On this page" in the right sidebar folds every code block on the page, then
reads "Unfold all code" and opens them all. Code a notebook hides itself (the `hide-input` tag) folds and unfolds
with the rest, and a cell's output is never folded. Pages without code blocks get no button.

## Heading links

Clicking the `#` after a heading copies a link to that section, as well as going to it, and
"Copied" shows beside it for a moment. Copying needs a secure page (https, or localhost when
previewing); elsewhere the `#` is a plain link.

## Tables

Table columns are left-aligned. In a MyST table, colons in the separator row set a column's
alignment: `:---` left, `:---:` center, `---:` right. Right-align columns of quantities, so that
digits of the same place value line up. Right-aligned cells use tabular figures:

```markdown
| Channel     | Samples |
| :---------- | ------: |
| temperature |  12,000 |
| pressure    |     450 |
```

pandas DataFrames in notebook outputs are right-aligned, as in Jupyter.

## Mermaid diagrams

The theme sets up [sphinxcontrib-mermaid](https://github.com/mgaitan/sphinxcontrib-mermaid), so a
```` ```mermaid ```` fence is a diagram, with no entry in `extensions`. Each diagram is as tall as its
content. A diagram can set its options in Mermaid's own front matter, as VS Code's preview and
GitHub read it:

````markdown
```mermaid
---
config:
  layout: elk
name: stack-diagram
---
flowchart TB
```
````

`config` and `title` become the directive's options, and `name` the diagram's HTML id, for a
stylesheet to style one diagram.

In dark mode, diagrams keep the colors of Mermaid's dark theme; Shibuya would otherwise invert them.
The fullscreen button is an icon in the diagram's bottom-right corner.

## Links in code

The theme sets up [sphinx-codeautolink](https://sphinx-codeautolink.readthedocs.io) and
`sphinx.ext.intersphinx`, with no entries in `extensions`: names in Python code blocks and notebook
cells link to their API docs. A name links when the project documents it, or when a site in
`intersphinx_mapping` does. `intersphinx()` gives the entries for Nominal's docs sites:

```python
from nominal_sphinx_theme import intersphinx

intersphinx_mapping = {
    **intersphinx("nominal", "instro"),  # nominal-client's docs and instro's
    "python": ("https://docs.python.org/3", None),
}
```

The names it knows are in `DOCS_SITES`. Links keep the code's colors and are underlined on hover.
sphinx-codeautolink's settings (`codeautolink_*`) go in `conf.py` as usual; its warnings are off
unless a project turns them on, and a Python block it can't parse, such as a signature with types
(`name: str = ...`), stays unlinked without a warning. To leave a block unlinked, put
[`autolink-skip`](https://sphinx-codeautolink.readthedocs.io/en/stable/reference.html) before it.

## Code fences in docstrings

autodoc and sphinx-autoapi read docstrings as reStructuredText, so a Markdown ```` ``` ```` fence in
a docstring doesn't render as code. In a repo whose docstrings use fences, add the theme's
`docstring_fences` module to `extensions`. Unlike the theme's other features, it's off unless listed:

```python
extensions = [..., "nominal_sphinx_theme", "nominal_sphinx_theme.docstring_fences"]
```

Each fence becomes a code block, in the fence's language, before Napoleon reads the docstring's
sections. With sphinx-click loaded, command descriptions get the same.

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
| [`bump-theme.yml`](.github/workflows/bump-theme.yml) | Called by each repo that uses the theme | Moves that repo's `uv.lock` and its pins on this repo to the theme's newest commit, in one PR |
| [`docs-gate.yml`](.github/workflows/docs-gate.yml) | Called by each repo's docs workflow | The check that stops a bump PR merging when the docs don't build |
| [`bump-all.yml`](.github/workflows/bump-all.yml) | By hand | Runs every repo's bump now |
| [`docs-preview`](.github/actions/docs-preview/action.yml) (action) | A step in each repo's docs build | Uploads the built docs and links the PR's preview as a commit status |

### Theme updates

Each repo using the theme pins a commit of it in `uv.lock`. A daily workflow there, calling
`bump-theme.yml`, runs `uv lock --upgrade-package nominal-sphinx-theme`. It then moves each pin on
this repo in `.github/workflows`, such as `bump-theme.yml@<sha> # main, <date>`, to the same commit
and that commit's date. If either changes, NomBot opens one PR, `chore(deps): bump nominal-sphinx-theme to <sha>`, from the branch
`chore/bump-nominal-sphinx-theme`, or updates the one already open. The PR merges itself once the
repo's required checks pass.

- **NomBot:** the workflow mints a NomBot App token. A PR opened with `GITHUB_TOKEN` wouldn't run the
  repo's other workflows, so its docs wouldn't be checked. The token has `workflows:write`, because
  GitHub refuses a push that changes `.github/workflows` without it.
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

- **Pins:** pin `uses:` to a commit of this repo, as for any action, with the comment
  `# main, <date>`, the commit's date. This repo has no releases, so Dependabot can't move the pin.
  The bump moves it, but only with that comment: it leaves any other pin as it is.
- **Secrets:** pass the two NomBot secrets, not `secrets: inherit`, which hands every secret in the
  repo to this repo's workflow. Semgrep blocks `secrets: inherit`.
- **Permissions:** a called workflow can't have more `GITHUB_TOKEN` permissions than its caller.
  `bump-theme.yml` asks for `contents: read`, and `docs-gate.yml` for none.

### Docs previews

The renderdoc Cloudflare Worker serves a PR's built docs, from its artifact, at
`https://renderdoc.cloudflare-admins.workers.dev/<owner>/<repo>/pull/<n>/`. The `docs-preview`
action, as the last step of the docs build, gives each PR a link to it:

- If the build passed, it uploads the site as the `docs-site` artifact and sets the commit status
  `docs preview` to success, linked to the preview.
- If the build failed or was cancelled, it sets the status to failure or error, linked to the run.
- On a PR from a fork, it uploads the site but sets no status: the PR's token is read-only, and the
  Worker serves only PRs from branches in the repo.
- On other events it does nothing.

Add it to the job that builds the docs on PRs, after the build:

```yaml
permissions:
  contents: read
  statuses: write

    steps:
      # ...build the docs...
      - name: "Built docs: upload and preview"
        if: always() && github.event_name == 'pull_request'
        uses: nominal-io/nominal-sphinx-theme/.github/actions/docs-preview@<commit> # main, <date>
        with:
          path: docs/_build/dirhtml
          job-status: ${{ job.status }}
          # artifact: docs-site   # must match the repo's `artifact` in the Worker's REPOS
          # retention-days: 30    # how long the preview stays
```

The step needs `if: always()` to run after a failed build, and `job-status`, because an action can't
read the job's status. The Worker must allow the repo; `nominal-io/*` is allowed.

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
- [`hub.md`](skills/nominal-docs/hub.md) is for repos whose docs dev.nominal.io publishes: where things go, and how theme updates reach them. It names `sites.toml` in dev.nominal.io as the list of those repos rather than copying it.
- The Style section and the docstring files are written by people. Change them through a PR here.

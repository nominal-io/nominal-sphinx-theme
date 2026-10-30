# Docs in the dev.nominal.io hub

For repos whose docs the hub publishes: each `[[project]]` in
[`sites.toml`](https://github.com/nominal-io/dev.nominal.io/blob/main/sites.toml) in
nominal-io/dev.nominal.io. That file is the list of these repos. Read it there rather than copy it.

## Publishing

- The hub serves the repo's docs at `/{lang}/{project}/`, set in `sites.toml`, not by the repo's name.
- It pulls the latest docs build from the repo's default branch on each of its runs. A merged change
  shows on the hub after its next run.
- Keep links relative, as Sphinx writes them, so they work under `/{lang}/{project}/` and in the
  hub's offline copy.

## Theme or repo

The repo uses nominal-sphinx-theme, so its docs look like the rest of the hub.

- Something every repo using the theme should share goes in the theme, through a PR to
  nominal-io/nominal-sphinx-theme: the look, fixes to Shibuya or to shared extensions, directives
  more than one repo uses, and default Sphinx and MyST settings. Its README, "What goes in the
  theme", has the rule.
- Don't override the theme's templates, such as `partials/site-head.html`, or restyle its header in
  the repo. Change the theme instead.
- Something only this repo's docs need stays in the repo.
- Something another repo already has, such as a stylesheet or an extension, moves to the theme
  rather than being copied.
- Docs also published outside the hub set `nominal_hub_url = "https://dev.nominal.io/"`, so the
  header links back to the hub.

## Theme updates

- A daily `bump-theme.yml` run opens a PR, `chore(deps): bump nominal-sphinx-theme to <sha>`, which
  merges itself once the repo's required checks pass, unless its ruleset needs an approval. The
  docs gate stops it merging if the docs don't build.
- To preview an unmerged theme change, build against a local checkout of the theme with
  `uv run --with-editable <path to nominal-sphinx-theme> sphinx-build ...`.

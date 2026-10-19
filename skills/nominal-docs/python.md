# Python docstrings

<!-- Human-owned. Agents: don't edit this file. Suggest changes in chat instead. -->

## Format

- Google style.
- All new code gets docstrings.
- Concise and clear.

## Content

- Args and returns state their types, and units where they apply.
- Classes: the `__init__` docstring gives a full usage example.
- Unsure what something means? Don't guess. Leave it out and add `TODO: add doc`.

## Markup

Docstrings are reStructuredText, rendered by Sphinx.

- Literals: double backticks, ``` ``code`` ```.
- Links to other code: single backticks, `` `Measurement` ``, or a role, `` :class:`~instro.lib.types.Measurement` ``.
- No Markdown links and no mkdocstrings `[Name][path]` references. They don't render.
- `Returns:` sections: continuation lines keep the first line's indent.

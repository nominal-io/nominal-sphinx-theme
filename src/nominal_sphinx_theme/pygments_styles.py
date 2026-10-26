"""Atom's One Light and One Dark (github.com/atom/one-light-syntax, github.com/atom/one-dark-syntax) as
Pygments styles: each theme's palette from its colors.less, mapped to tokens as its _base.less does.

Sphinx takes a style by its dotted path, e.g. ``nominal_sphinx_theme.pygments_styles.OneDarkStyle``.
"""

from pygments.style import Style
from pygments.token import (
    Comment,
    Error,
    Escape,
    Generic,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
)


def _styles(p: dict[str, str]) -> dict:
    """Pygments token styles from an Atom One palette (mono-1..3, hue-1..6-2)."""
    return {
        Text: p["mono1"],
        Error: p["hue5"],
        Escape: p["hue1"],
        Comment: f"italic {p['mono3']}",
        Keyword: p["hue3"],
        Keyword.Constant: p["hue6"],
        Operator: p["mono1"],
        Operator.Word: p["hue3"],
        Punctuation: p["mono1"],
        Name: p["mono1"],
        Name.Attribute: p["hue6"],
        Name.Builtin: p["hue1"],
        Name.Builtin.Pseudo: f"italic {p['hue5']}",
        Name.Class: p["hue6_2"],
        Name.Constant: p["hue6"],
        Name.Decorator: p["hue2"],
        Name.Exception: p["hue6_2"],
        Name.Function: p["hue2"],
        Name.Function.Magic: p["hue1"],
        Name.Tag: p["hue5"],
        Name.Variable: p["hue5"],
        String: p["hue4"],
        String.Escape: p["hue1"],
        String.Interpol: p["hue5_2"],
        String.Regex: p["hue1"],
        Number: p["hue6"],
        Generic.Deleted: p["hue5"],
        Generic.Emph: "italic",
        Generic.Error: p["hue5"],
        Generic.Heading: f"bold {p['hue2']}",
        Generic.Inserted: p["hue4"],
        Generic.Output: p["mono2"],
        Generic.Prompt: p["mono3"],
        Generic.Strong: "bold",
        Generic.Subheading: p["hue2"],
        Generic.Traceback: p["hue5"],
    }


class OneDarkStyle(Style):
    """Atom One Dark."""

    name = "atom-one-dark"
    background_color = "#282c34"
    highlight_color = "#2c313c"
    styles = _styles(
        {
            "mono1": "#abb2bf",
            "mono2": "#828997",
            "mono3": "#5c6370",
            "hue1": "#56b6c2",
            "hue2": "#61afef",
            "hue3": "#c678dd",
            "hue4": "#98c379",
            "hue5": "#e06c75",
            "hue5_2": "#be5046",
            "hue6": "#d19a66",
            "hue6_2": "#e5c07b",
        }
    )


class OneLightStyle(Style):
    """Atom One Light."""

    name = "atom-one-light"
    background_color = "#fafafa"
    highlight_color = "#f0f0f1"
    styles = _styles(
        {
            "mono1": "#383a42",
            "mono2": "#696c77",
            "mono3": "#a0a1a7",
            "hue1": "#0184bc",
            "hue2": "#4078f2",
            "hue3": "#a626a4",
            "hue4": "#50a14f",
            "hue5": "#e45649",
            "hue5_2": "#ca1243",
            "hue6": "#986801",
            "hue6_2": "#c18401",
        }
    )

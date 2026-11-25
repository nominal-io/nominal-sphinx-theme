"""Google Analytics on the pages: Google's tag (gtag.js). The docs hub adds the same tag to pages built
without it, from src() and script().
"""

# dev.nominal.io's GA4 measurement ID
ID = "G-6KQ94CEW2M"


def src(ga_id: str) -> str:
    """The URL of Google's tag, loaded async."""
    return f"https://www.googletagmanager.com/gtag/js?id={ga_id}"


def script(ga_id: str) -> str:
    """The script for a page, after the tag from src()."""
    return (
        "window.dataLayer = window.dataLayer || [];"
        "function gtag() { dataLayer.push(arguments); }"
        f'gtag("js", new Date()); gtag("config", "{ga_id}");'
    )

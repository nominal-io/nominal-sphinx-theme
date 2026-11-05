from nominal_sphinx_theme import theme_options

REPO = "https://github.com/nominal-io/demo"
TABS = [{"title": "Guides", "url": "index"}, {"title": "Examples", "url": "examples/index"}]


def test_github_tab_ends_the_tabs():
    assert theme_options(github_url=REPO, nav_links=TABS)["nav_links"] == [*TABS, {"title": "GitHub", "url": REPO}]


def test_no_github_tab_when_off_without_tabs_or_without_a_repo():
    assert theme_options(github_url=REPO, nav_links=TABS, github_tab=False)["nav_links"] == TABS
    assert "nav_links" not in theme_options(github_url=REPO)
    assert theme_options(nav_links=TABS)["nav_links"] == TABS
    assert "github_tab" not in theme_options(github_url=REPO)


def test_a_project_s_own_github_tab_is_not_repeated():
    links = [*TABS, {"title": "Code", "url": REPO + "/"}]
    assert theme_options(github_url=REPO, nav_links=links)["nav_links"] == links

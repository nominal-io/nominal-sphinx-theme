# Recipes run in PowerShell on Windows (no bash or cygpath needed) and sh elsewhere.
[windows]
set shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

# list the recipes
default:
    @just --list

# install the theme and its test dependencies
setup:
    uv sync --group dev

# run the tests, as in CI
test:
    uv run --group dev pytest

# build the wheel and sdist into dist/
build:
    uv build

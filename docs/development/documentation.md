# Documentation

Project uses Sphinx to generate documentation from docstrings (documentation in-code) and custom pages written in Markdown (through the [MyST parser](https://myst-parser.readthedocs.io/en/latest/)).

## Build documentation website

To build it:

```sh
# install aditionnal dependencies
python -m pip install -U -e .[doc]
# build it
sphinx-build -b html docs docs/_build/html
# optimized (quiet, multiprocessing, doctrees separated)
sphinx-build -b html -d docs/_build/cache -j auto -q docs docs/_build/html
```

Open `docs/_build/index.html` in a web browser.

## Write documentation using live render

```sh
sphinx-autobuild -b html docs/ docs/_autobuild/ --delay 3 --open-browser --ignore docs/misc/dependencies.md --ignore docs/reference/rules_context.json --ignore docs/usage/download_section.md
```

Your default web browser should be automatically opened on <http://localhost:8000> displaying the HTML render which will be  updated when a file is saved.

---

## Deploy documentation website

Documentation website is hosted on GitHub Pages for every commit pushed on main branch.

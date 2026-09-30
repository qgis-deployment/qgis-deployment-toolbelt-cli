# Develop on Ubuntu

Commands tested on:

- Ubuntu 24.04
- Ubuntu 26.04

## Install Python and Git

Install system requirements:

```sh
sudo apt install git python3-pip python3-virtualenv python3-venv virtualenv
```

Clone the repository where you want:

```sh
git clone https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli.git
# or using ssh
git clone git@github.com:qgis-deployment/qgis-deployment-toolbelt-cli.git
```

Create and enter virtual environment (change the path at your convenience):

```sh
python3 -m venv .venv
source .venv/bin/activate
```

## Install project requirements

```sh
python -m pip install -U pip setuptools wheel
# dulwich without binary extensions, like official executables
PIP_NO_BINARY=dulwich PURE=1 python -m pip install -U -e .[dev]
```

> [!NOTE]
> As in CI and official executables, [dulwich](https://pypi.org/project/dulwich/) is installed without its Rust extensions: `PIP_NO_BINARY` makes pip build it from source, `PURE` skips the extensions.

## Install git hooks

```sh
pre-commit install
```

## Try it

```sh
qgis-deployment-toolbelt --help
```

Happy coding!

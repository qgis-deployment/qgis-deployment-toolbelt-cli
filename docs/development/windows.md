# Develop on Windows

Commands tested on:

- Windows 11 Professional

## Requirements

- [Python 3.10+](https://www.python.org/downloads/windows/)
- [Git](https://git-scm.com/download/win) and/or [GitHub Desktop](https://desktop.github.com/)

## Enable remote scripts (for virtual environment)

Open a Powershell prompt as **administrator** inside the repository folder:

```powershell
# if not already done, enable scripts - required by virtualenv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Installation steps

### Clone the repository

Clone the repository where you want using [GitHub Desktop](https://docs.github.com/en/desktop/installing-and-configuring-github-desktop/installing-and-authenticating-to-github-desktop/setting-up-github-desktop) as graphical interface or a PowerShell terminal:

```powershell
git clone https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli.git
# or using ssh
git clone git@github.com:qgis-deployment/qgis-deployment-toolbelt-cli.git
```

### Set up the virtual environment

```powershell
# create a virtual env
py -3 -m venv .venv

# enable virtual env
.\.venv\Scripts\activate

# upgrade basic tooling
python -m pip install -U pip setuptools wheel

# dulwich without binary extensions, like official executables
$env:PIP_NO_BINARY = "dulwich"; $env:PURE = "1"
python -m pip install -U -e .[dev]
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

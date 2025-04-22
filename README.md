# QGIS Deployment CLI

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![flake8](https://img.shields.io/badge/linter-flake8-green)](https://flake8.pycqa.org/)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/qgis-deployment/qgis-deployment-toolbelt-cli/main.svg)](https://results.pre-commit.ci/latest/github/qgis-deployment/qgis-deployment-toolbelt-cli/main)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Guts_qgis-deployment-cli&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Guts_qgis-deployment-cli)

[![🎳 Tester](https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/actions/workflows/tests.yml/badge.svg)](https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/qgis-deployment/qgis-deployment-toolbelt-cli/branch/main/graph/badge.svg?token=ZHGRNMA7TV)](https://codecov.io/gh/qgis-deployment/qgis-deployment-toolbelt-cli)
[![📦 Build & 🚀 Release](https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/actions/workflows/build_release.yml/badge.svg?branch=main)](https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/actions/workflows/build_release.yml)

[![PyPi version badge](https://badgen.net/pypi/v/qgis-deployment-toolbelt)](https://pypi.org/project/qgis-deployment-toolbelt/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/qgis-deployment-toolbelt)](https://pypi.org/project/qgis-deployment-toolbelt/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/qgis-deployment-toolbelt)](https://pypi.org/project/qgis-deployment-toolbelt/)

Cross-platform (but Windows focused) CLI to perform deployment operations related to QGIS: profiles, plugins, etc.

## Try it quickly

Using Python and the official package installer `pip`:

```sh
pip install qgis-deployment-toolbelt
qdt -s https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/raw/main/examples/scenarios/demo-scenario.qdt.yml
```

Or using a pre-built executable (downloadable [through releases assets](https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/releases/latest)). For example on Windows:

```powershell
QGISDeploymentToolbelt_0-27-0_Windows.exe -s https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/raw/main/examples/scenarios/demo-scenario.qdt.yml
```

Look for new icons in start menu or desktop!

**Interested**? For further details, [read the documentation](https://qgis-deployment.github.io/qgis-deployment-toolbelt-cli/) :books:.

## Contribute

Read the [contribution guidelines](CONTRIBUTING.md) and the documentation.

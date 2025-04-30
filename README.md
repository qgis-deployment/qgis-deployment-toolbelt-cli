<div align="center">
  <a href="https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli">
    <img alt="QDT logo" src="docs/static/logo_qdt.png" height="120">
  </a>
</div>

# QGIS Deployment Toolbelt (QDT)

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

**QGIS Deployment Toolbelt (QDT)** is a cross-platform (primarily Windows-focused) command-line tool that streamlines the deployment and management of **QGIS profiles**, **plugins**, and related settings within organizations.

It helps **standardize** user environments, **simplify** updates, and **integrate** with IT deployment strategies like **GPO**, **SCCM**, or **InTune**.

## ⭐ Why QDT?

- Save hours of manual QGIS configuration and profile management
- Reduce configuration errors and user friction
- Scale QGIS deployments in professional environments easily

## ✨ Features

- **Manage QGIS profiles easily**: define, store, and deploy profiles with a simple `profile.json` file.
- **Version control integration**: Git-powered backend for tracking changes and enabling collaborative profile management.
- **IT-friendly**: designed to work with Active Directory, GPOs, SCCM, InTune, and other enterprise tools.
- **Seamless user experience**: deliver a consistent QGIS experience across your organization with minimal friction.
- **Advanced configuration handling**: use variabilized `QGIS3.ini` files to handle dynamic or environment-specific settings.
- **Conditional deployments**: deploy specific profiles based on rules, environment variables, or user criteria.
- **Optimized plugin management** : reduce bandwidth usage by rationalizing plugin downloads and installations.

## 🚀 Try it quickly

You have multiple options to try QDT:

- Using Python and the official modern CLI installer [pipx](https://pipx.pypa.io/):

    ```sh
    pipx run qgis-deployment-toolbelt -s https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/raw/main/examples/scenarios/demo-scenario.qdt.yml
    ```

- Using Python and the official package installer `pip`:

    ```sh
    pip install qgis-deployment-toolbelt
    qdt -s https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/raw/main/examples/scenarios/demo-scenario.qdt.yml
    ```

- Using a pre-built executable (downloadable [through releases assets](https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/releases/latest)). For example on Windows:

    ```powershell
    ./Windows_QGISDeploymentToolbelt_0-37-0.exe  -s https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/raw/main/examples/scenarios/demo-scenario.qdt.yml
    ```

Once completed, check:

- The **Start menu** / **Desktop** for new shortcuts.
- The **QGIS Profiles menu** for new profiles.

![QGIS - List of profiles with ones added by QDT demonstration scenario](./docs/static/examples_qgis_profiles_menu.png)

Splash screen when launching the **Demo Profile**:

![QGIS splash screen - QDT Demo Profile](./examples/profiles/demo/images/splash.png)

Splash screen for the **Viewer Profile**:

![QGIS splash screen - QDT Viewer Profile](./examples/profiles/Viewer%20Mode/images/splash.png)

Have you tried it on Linux? Well, you should find an additional profile simply named "QDT Only Linux".

> [!TIP]
> **Interested**? For further details, [read the documentation](https://qgis-deployment.github.io/qgis-deployment-toolbelt-cli/) :books:.

## 🤝 Contribute

Want to help?

Check out the [contribution guide and "Development" section in the documentation](https://qgis-deployment.github.io/qgis-deployment-toolbelt-cli/development/contribute.html).

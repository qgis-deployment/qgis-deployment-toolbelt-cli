# {{ title }} (QDT) - Documentation

> **Description:** {{ description }}  
> **Author and contributors:** {{ author }}  
> **Source code:** {{ repo_url }}  
> **License:** {{ license }}  
> **Last released version:** {{ release }}  
> **Current version:** {{ version }}  
> **Last documentation build:** {{ date_update }}

[![PyPi version badge](https://badgen.net/pypi/v/qgis-deployment-toolbelt)](https://pypi.org/project/qgis-deployment-toolbelt/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/qgis-deployment-toolbelt)](https://pypi.org/project/qgis-deployment-toolbelt/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/qgis-deployment-toolbelt)](https://pypi.org/project/qgis-deployment-toolbelt/)

<!-- markdownlint-disable MD034 -->

::::{grid} 3
:gutter: 2

:::{grid-item}

```{button-link} https://matrix.to/#/#qdt:matrix.org/
:color: primary
:shadow:
:expand:
:tooltip: Matrix channel for QDT

{fa}`comments` Matrix channel
```

:::

:::{grid-item}

```{button-link} https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/discussions/categories/q-a
:color: success
:expand:
:shadow:
:tooltip: Github discussions page

{fab}`github` Discussions on GitHub
```

:::

:::{grid-item}

```{button-link} mailto:qgis+qdt@oslandia.com
:color: secondary
:expand:
:shadow:
:tooltip: mailto Oslandia about QDT
{material-regular}`mail;1.5em` Contact us by email
```

:::{grid-item}
:::

::::
<!-- markdownlint-enable MD034 -->

----

![QGIS Deployment Toolbelt CLI](./static/qgis-deployment-toolbelt_cli_help.png)

## They use QDT

```{include} misc/_references_carousel.md
```

## What it is and the underlying philosophy

Development is leaded by the following principles and goals:

- a tailor-made tool for QGIS ecosystem
- open source and community driven
- independant from the QGIS installation mode
- packaged as CLI and prebuilt stand-alone binary
- cross-platform but with a strong focus on Windows
- documented
- tested
- usable with a single action (*one-click run*)
- easily reusable
- easily maintenable
- compatible with automation mechanisms:
    - cron / scheduled tasks
    - Windows [groups policies](https://en.wikipedia.org/wiki/Group_Policy) (so called GPO for *Group Policies Object*) and [tooling around client management](https://learn.microsoft.com/en-us/windows/client-management/)
- flexible enough to be adapted to an internal security policy (allowing to put a custom code certificate)

### It's not

- an installer for QGIS
- a packager helper

----

## Quickstart

### With Python

1. Get QDT executable:

    The best way to install it is using [pipx](https://pipx.pypa.io/stable/):

    ```sh
    pipx install -U qgis-deployment-toolbelt
    ```

    If you don't have installed pipx, it's obviously still installable with pip but you'll have to deal with checking that the Python scripts folder is declared in your `PATH` (list of folders where executables are authorized to run).

    ```sh
    pip install -U qgis-deployment-toolbelt
    ```

1. Run a scenario. For example the one which is shipped as demonstration in QDT project:

    ```sh
    qdt -s https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/raw/main/examples/scenarios/demo-scenario.qdt.yml
    ```

You can also run it directly with pipx:

```sh
pipx run qgis-deployment-toolbelt --help
pipx run qgis-deployment-toolbelt -s https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/raw/main/examples/scenarios/demo-scenario.qdt.yml
```

### With the stand-alone executable

> Typically on Windows

1. Download latest version that matches your environment from [releases](https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/releases/latest)
1. Open a terminal in the same folder
1. Rename 'Windows_QGISDeploymentToolbelt_{{ release | replace(".","-")  }}' as `qdt.exe`:

    ```powershell
    mv *_QGISDeploymentToolbelt_* qdt.exe
    ```

1. Run a scenario. For example the one which is shipped as demonstration in QDT project:

    ```powershell
    ./qdt.exe -s https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/raw/main/examples/scenarios/demo-scenario.qdt.yml
    ```

> Typically on Ubuntu

1. Download latest version that matches your environment from [releases](https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/releases/latest)
1. Open a terminal in the same folder
1. Rename 'Ubuntu_QGISDeploymentToolbelt_{{ release | replace(".","-")  }}' it as `qdt.bin`:

    ```sh
    mv *_QGISDeploymentToolbelt_* qdt.bin
    ```

1. Make sure it's runnable:

    ```sh
    chmod u+x ./qdt.bin
    ```

1. Run a scenario. For example the one which is shipped as demonstration in QDT project:

    ```sh

    ./qdt.bin -s https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/raw/main/examples/scenarios/demo-scenario.qdt.yml
    ```

----

## Table of contents

```{toctree}
---
caption: How to use
maxdepth: 1
---
usage/installation
usage/how_it_works
usage/how_to_use
usage/profile
usage/scenario
jobs/index
usage/cli
usage/settings
```

```{toctree}
---
caption: Guides
glob:
maxdepth: 1
---
guides/howto_download_latest_qdt_exe.md
guides/howto_check_qdt_binary_certificate
guides/howto_validate_profiles_scenarios
guides/howto_behind_proxy
guides/howto_use_custom_ssl_certs
guides/howto_manage_private_git
guides/howto_publish_http
guides/howto_qgis_get_plugin_id
guides/howto_schedule_deployment
guides/*
guides/howto_windows_sign_executable
```

```{toctree}
---
caption: Reference
glob:
maxdepth: 1
---
reference/*
```

```{toctree}
---
caption: Miscellaneous
maxdepth: 1
---
misc/examples
misc/references
misc/security
misc/compatibility
misc/credits
misc/funding
```

----

## Want to contribute?

```{toctree}
---
caption: Development
maxdepth: 1
---
Code documentation <_apidoc/modules>
development/contribute
development/ubuntu
development/windows
development/documentation
development/testing
development/packaging
development/signing_binary
development/releasing
development/history
```

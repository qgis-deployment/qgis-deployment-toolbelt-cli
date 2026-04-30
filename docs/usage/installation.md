# Installation

## As a stand-alone executable

### Requirements

- operating system:
    - Linux (tested on Debian-based distribution)
    - Windows 10+
- network:
    - github.com
    - pypi.org

### Step-by-step

1. Download the latest release from [GitHub Release](https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/releases/latest):

  ```{include} download_section.md
  ```

1. Make sure that it's executable (typically on Linux: `chmod u+x ./QGISDeploymentToolbelt_XXXXXX`)
1. Elaborate your scenario (or [grab the sample from the repository](https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/blob/main/scenario.qdt.yml))
1. Run it:
    - from your favorite shell if you like the CLI - see [the relevant section](./cli.md)
    - store your scenario as `scenario.qdt.yml` in the same folder and double-click on the executable

:::{warning}
MacOS version is not tested and is just here to encourage beta-testing and feedback to improve it.
:::

----

## As a Python package

### Requirements

- Python 3.10+

### Step-by-step

The package is installable with pip:

```sh
pip install qgis-deployment-toolbelt
```

It's then available as a CLI: see [the relevant section](./cli.md)

----

## Using Docker

:::{warning}
The Docker image is **not** a substitute for the standalone binary or Python package when deploying to end-user workstations. It is more designed for **server-side and CI/CD usage** only.

See [deatils below](#scope-and-limitations).
:::

The package is published as container on GitHub Container Registry (GHCR):

```sh
docker pull ghcr.io/qgis-deployment/qgis-deployment-toolbelt-cli
```

See [container page for additional options and instructions](https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pkgs/container/qgis-deployment-toolbelt-cli).

### Scope and limitations

QDT is designed to run **on** the end-user machine, not alongside it. A container is an isolated environment: it does not share the host's desktop session, Windows registry, or shell environment. Consequently, several jobs behave differently or are entirely unavailable depending on the execution context.

| Job | From a container | Comments |
| :-- | :--------------: | :------- |
| `qplugins-downloader` | **X** | Requires a bind mount on the cache path |
| `qplugins-synchronizer` | **X** | Requires a bind mount on the QGIS profiles path |
| `qprofiles-downloader` | **X** | Requires a bind mount on the target path |
| `qprofiles-synchronizer` | **X** | Requires a bind mount on the QGIS profiles path |
| `default-profile-setter` | *-* | Works if the QGIS profiles folder is bind-mounted |
| `manage-env-vars` | *-* | Writes to the mounted file but changes have no effect on already-running host processes |
| `splash-screen-manager` | *-* | Works if the QGIS profiles folder is bind-mounted |
| `qgis-installation-finder` | 0 | QGIS is not installed inside the container |
| `shortcuts-manager` | 0 | Relies on desktop APIs (XDG, `win32com`) that are unavailable inside the container |

Legend:

- **X**: works with some configuration (see comments)
- *-*: works but has no effect on the host environment
- 0: does not work at all

#### Appropriate use cases for the Docker image

- **CI/CD pipelines**: validate scenario and `profile.json` files against the JSON schemas, or run integration tests in an isolated environment.
- **Server-side pre-caching**: run `qprofiles-downloader` and `qplugins-downloader` on a server to populate a shared network drive, which end-user machines then consume via the `git_local` or `http` protocol without Docker.

Example of use-cases, pre-download profiles and plugins to a shared network folder:

```sh
docker run --rm \
  -v /srv/qdt-cache:/home/qdt-srv/.cache/qgis-deployment-toolbelt \
  -v $(pwd)/scenario.qdt.yml:/home/qdt-srv/scenario.qdt.yml \
  qdt:latest deploy -s scenario.qdt.yml
```

For all other use cases, in particular for deploying to end-user workstations, use the [standalone binary](../usage/installation.md#as-a-stand-alone-executable) or [pip install](../usage/installation.md#as-a-python-package).

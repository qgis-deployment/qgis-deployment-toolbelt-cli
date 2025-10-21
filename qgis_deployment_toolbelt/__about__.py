#! python3  # noqa: E265

"""Package's metadata to easily retrieve informations about it.
See: https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html#dynamic-metadata
"""

# standard lib
import logging
from datetime import date
from importlib import metadata
from os import getenv
from pathlib import Path
from shutil import which
from subprocess import check_output


logger = logging.getLogger(__name__)

# import metadata from installed package, if possible
_pkg_metadata = metadata.metadata("qgis-deployment-toolbelt") or {}

try:
    from ._version import version as __version__
except ImportError:
    __version__ = _pkg_metadata.get("Version", "0.0.0-dev0")


# store metadata into module attributes
__author__: str = _pkg_metadata.get(
    "Maintainer-email",
    "Julien Moura (Oslandia), Jean-Marie Kerloch (Oslandia), Nicolas Godet (ISL)",
)
__copyright__: str = f"2021 - {date.today().year}, {__author__}"
__executable_name__ = __package_name__ = _pkg_metadata.get(
    "Name", "qgis-deployment-toolbelt"
)
__license__: str = _pkg_metadata.get("License-Expression", "Apache-2.0")
__summary__ = (
    "QGIS Deployment Toolbelt (QDT) is a CLI (Command Line Interface) "
    "to perform redundant operations after a QGIS deployment, "
    "managing QGIS profiles, plugins, environment variables, "
    "start menu / desktop shortcuts and many things to rationalize your QGIS installations."
)
__title__ = "QGIS Deployment Toolbelt"
__title_clean__ = "".join(e for e in __title__ if e.isalnum())
__uri_homepage__ = "https://qgis-deployment.github.io/qgis-deployment-toolbelt-cli/"
__uri_repository__ = "https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/"
__uri__ = __uri_repository__
__version_clean__: str = __version__.split(".dev")[0].split("+")[0]
__version_info__ = tuple(
    [
        int(num) if num.isdigit() else num
        for num in __version__.replace("-", ".", 1).split(".")
    ]
)

__all__ = [
    "__author__",
    "__copyright__",
    "__license__",
    "__summary__",
    "__title__",
    "__uri__",
    "__version__",
]

# get latest git tag if possible, if not fallback to __version__
release: str | None = None
try:
    github_ref = getenv("GITHUB_REF", "")
    if github_ref.startswith("refs/tags/"):
        release = github_ref[len("refs/tags/") :]
        logger.debug("Git tag found from GITHUB_REF:", release)
    elif git_path := which("git"):
        release = (
            check_output(
                [git_path, "describe", "--tags", "--abbrev=0"],
                cwd=Path(__file__).parent.resolve(),
            )
            .decode()
            .strip()
        )
        logger.debug("Git tag found from git:", release)
except Exception:
    logger.debug("No git tag found, fallback to __version__")
    release = __version_clean__

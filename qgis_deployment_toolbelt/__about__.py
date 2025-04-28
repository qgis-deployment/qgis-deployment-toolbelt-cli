#! python3  # noqa: E265

"""
Metadata bout the package to easily retrieve informations about it.
See: https://packaging.python.org/guides/single-sourcing-package-version/
"""

from datetime import date

__all__ = [
    "__author__",
    "__copyright__",
    "__email__",
    "__license__",
    "__summary__",
    "__title__",
    "__uri__",
    "__version__",
]

__author__ = (
    "Julien Moura (Oslandia), Jean-Marie Kerloch (Oslandia), Nicolas Godet (ISL)"
)
__copyright__ = f"2021 - {date.today().year}, {__author__}"
__email__ = "qgis@oslandia.com"
__executable_name__ = "qgis-deployment-toolbelt"
__package_name__ = "qgis-deployment-toolbelt"
__keywords__ = ["cli", "deployment", "profiles", "qdt", "QGIS"]
__license__ = "Apache-2.0"
__summary__ = (
    "QGIS deployment toolbelt is a CLI (Command Line Interface) to perform "
    "redundant operations after a QGIS deployment."
)
__title__ = "QGIS Deployment Toolbelt"
__title_clean__ = "".join(e for e in __title__ if e.isalnum())
__uri_homepage__ = "https://qgis-deployment.github.io/qgis-deployment-toolbelt-cli/"
__uri_repository__ = "https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/"
__uri_tracker__ = f"{__uri_repository__}issues/"
__uri__ = __uri_repository__

__version__ = "0.37.0"
__version_info__ = tuple(
    [
        int(num) if num.isdigit() else num
        for num in __version__.replace("-", ".", 1).split(".")
    ]
)

#! python3  # noqa: E265

"""
Helper to determine whether the current Python interpreter is running
as frozen/bundled application (i.e. PyInstaller, cx_Freeze...) or not.

A "frozen" application is a Python program bundled into a standalone
executable using tools such as PyInstaller or cx_Freeze. These tools
typically set the ``sys.frozen`` attribute at runtime.

See: https://pyinstaller.org/en/latest/runtime-information.html#run-time-information
"""

# -- Imports --

# Standard library
import logging
import sys

# package
from qgis_deployment_toolbelt.__about__ import __package_name__


# -- Globals --

# logs
logger = logging.getLogger(__name__)

# -- Functions --


def is_frozen_app(log: bool = True) -> bool:
    """Determine whether the current Python process is running as a frozen application.

    Args:
        log (bool, optional): option to log result. Defaults to True.

    Returns:
        bool: True if the interpreter is running in a frozen context, False otherwise.
    """
    is_frozen = getattr(sys, "frozen", False)
    if not log:
        return is_frozen
    if is_frozen:
        logger.debug(f"{__package_name__} is running as frozen app.")
    else:
        logger.debug(f"{__package_name__} is not running as frozen app.")
    return is_frozen


def is_running_pyinstaller(log: bool = True) -> bool:
    """Determine whether the current process is running from a PyInstaller bundle.

    PyInstaller sets both:
        - ``sys.frozen`` (like other freezing tools)
        - ``sys._MEIPASS`` (temporary extraction directory or bundle path)

    Args:
        log (bool, optional): option to log result. Defaults to True.

    Returns:
        bool: True if executed from a PyInstaller-built executable, False otherwise.
    """
    is_pyinstaller = is_frozen_app(log=log) and hasattr(sys, "_MEIPASS")
    if not log:
        return is_pyinstaller
    if is_pyinstaller:
        logger.debug(
            f"{__package_name__} is running as frozen app packaged with PyInstaller."
        )
    else:
        logger.debug(f"{__package_name__} is not running from PyInstaller bundle.")
    return is_pyinstaller

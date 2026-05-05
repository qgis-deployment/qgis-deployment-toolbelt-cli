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


# -- Globals --

# logs
logger = logging.getLogger(__name__)

# -- Functions --


def is_frozen_app() -> bool:
    """Determine whether the current Python process is running as a frozen application.

    Returns:
        bool: True if the interpreter is running in a frozen context, False otherwise.
    """
    is_frozen = getattr(sys, "frozen", False)
    if is_frozen:
        logger.debug(f"{__name__}, {__package__} is running as frozen app.")
    else:
        logger.debug(f"{__name__}, {__package__} is not running as frozen app.")
    return is_frozen


def is_running_pyinstaller() -> bool:
    """Determine whether the current process is running from a PyInstaller bundle.

    PyInstaller sets both:
        - ``sys.frozen`` (like other freezing tools)
        - ``sys._MEIPASS`` (temporary extraction directory or bundle path)

    Returns:
        bool: True if executed from a PyInstaller-built executable, False otherwise.
    """
    is_pyinstaller = is_frozen_app() and hasattr(sys, "_MEIPASS")
    if is_pyinstaller:
        logger.debug(
            f"{__name__}, {__package__} is running as frozen app packaged with PyInstaller."
        )
    else:
        logger.debug(
            f"{__name__}, {__package__} is not running from PyInstaller bundle."
        )
    return is_pyinstaller

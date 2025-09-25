#! python3  # noqa: E265

"""
Shortcuts to exit CLI properly and with pretty messages.

Author: Julien Moura (github.com/guts)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
import sys

# project
from qgis_deployment_toolbelt.utils.journalizer import get_logger_filepath


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)

# #############################################################################
# ########## Functions #############
# ##################################


def exit_cli_error(message: str | Exception, abort: bool = True):
    """Display error message and stop execution.

    Args:
        message (Union[str, Exception]): message to log and display in terminal.
        abort (bool, optional): option to abort after displaying. Defaults to True.

    Raises:
        SystemExit: when abort is True
    """
    # log
    logger.error(message)
    logger.error(f"Please, read the full detailed log: {get_logger_filepath()}")

    # handle cases when the full exception is passed
    if isinstance(message, Exception):
        if isinstance(message.args, tuple) and len(message.args):
            message = message.args[0]
        else:
            message = getattr(message, "message", repr(message))
    if abort:
        sys.exit(message)


def exit_cli_normal(message: str | Exception, abort: bool = True):
    """Display normal message and stop execution if required.

    Args:
        message (Union[str, Exception]): message to log and display in terminal.
        abort (bool, optional): option to abort after displaying. Defaults to True.

    Raises:
        SystemExit: when abort is True
    """
    logger.info(message)

    if abort:
        sys.exit(0)


def exit_cli_success(message: str | Exception, abort: bool = True):
    """Display success message and stop execution ir required.

    Args:
        message (Union[str, Exception]): message to log and display in terminal.
        abort (bool, optional): option to abort after displaying. Defaults to True.

    Raises:
        SystemExit: when abort is True
    """
    logger.info(message)

    if abort:
        sys.exit(0)


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    pass

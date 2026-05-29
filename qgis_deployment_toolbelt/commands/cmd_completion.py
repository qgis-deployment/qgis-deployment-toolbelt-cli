#! python3  # noqa: E265
# SPDX-License-Identifier: Apache-2.0

"""Sub-command to generate shell completion scripts.

Author: Julien M. (https://github.com/guts)
"""


# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import importlib.util
import logging
import sys
from textwrap import dedent


# 3rd party
HAS_ARGCOMPLETE: bool = importlib.util.find_spec("argcomplete") is not None

# package
from qgis_deployment_toolbelt.__about__ import __executable_name__


# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)


COMPLETION_SNIPPETS: str = dedent(
    f"""
If you encountered register-python-argcomplete command not found error,
or if you are using zipapp, run

    pipx install 'gqis-deployment-toolbelt[completion]'

    or if you already installed QDT

    pipx inject qgis-deployment-toolbelt argcomplete

before running any of the following commands.


Add the appropriate command to your shell's config file
so that it is run on startup. You will likely have to restart
or re-login for the autocompletion to start working.

bash (in '~/.bashrc' or '~/.profile'):

    eval "$(register-python-argcomplete {__executable_name__})"

zsh:

    To activate completions in zsh, first make sure compinit is enabled:

    autoload -U compinit && compinit

    Afterwards you can enable completions for {__executable_name__}:

    eval "$(register-python-argcomplete {__executable_name__})"

tcsh:
    eval `register-python-argcomplete --shell tcsh {__executable_name__}`

fish:
    # Not required to be in the config file, only run once
    register-python-argcomplete --shell fish {__executable_name__} \\
        >~/.config/fish/completions/{__executable_name__}.fish

powershell:
    register-python-argcomplete --shell powershell {__executable_name__} | Out-String | Invoke-Expression
"""
).strip()

# ############################################################################
# ########## CLI #################
# ################################


def parser_completion(
    subparser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Set the argument parser for the completion subcommand.

    Args:
        subparser (argparse.ArgumentParser): parser to set up

    Returns:
        argparse.ArgumentParser: parser ready to use
    """

    subparser.set_defaults(func=run)

    return subparser


# ############################################################################
# ########## MAIN ################
# ################################


def run(args: argparse.Namespace) -> None:
    """Run the sub command logic.

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    logger.debug(f"Running {args.command} with {args}")

    if not HAS_ARGCOMPLETE:
        logger.error(
            "argcomplete is not installed. "
            "Run: pip install 'gqis-deployment-toolbelt[completion]'"
        )
        sys.exit(1)

    print(COMPLETION_SNIPPETS)  # noqa: T201

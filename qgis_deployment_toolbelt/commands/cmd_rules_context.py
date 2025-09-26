#! python3  # noqa: E265


"""
Sub-command to export local rules context.

Author: Julien M. (https://github.com/guts)
"""


# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import argparse
import logging
from pathlib import Path

# package
from qgis_deployment_toolbelt.constants import get_qdt_working_directory
from qgis_deployment_toolbelt.profiles.rules_context import QdtRulesContext
from qgis_deployment_toolbelt.utils.bouncer import exit_cli_error, exit_cli_success


# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)


# ############################################################################
# ########## CLI #################
# ################################


def parser_rules_context_export(
    subparser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Set the argument parser for subcommand.

    Args:
        subparser (argparse.ArgumentParser): parser to set up

    Returns:
        argparse.ArgumentParser: parser ready to use
    """

    subparser.add_argument(
        "-o",
        "--output",
        help="Path to the output file where to write rules context.",
        default=get_qdt_working_directory().joinpath("export/qdt_rules_context.json"),
        type=Path,
        dest="output_path",
    )

    subparser.set_defaults(func=run)

    return subparser


# ############################################################################
# ########## MAIN ################
# ################################


def run(args: argparse.Namespace):
    """Run the sub command logic.

    Open result of a previous command.

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    logger.debug(f"Running {args.command} with {args}")

    try:
        context_json_path = Path(args.output_path)
        context_json_path.parent.mkdir(parents=True, exist_ok=True)
        rules_context = QdtRulesContext()

        # write into the file passing extra parameters to json.dumps
        with context_json_path.open("w", encoding="UTF8") as wf:
            wf.write(rules_context.to_json(indent=4, sort_keys=True))

        # exit nicely
        print(f"Rules context exported in {args.output_path}")  # noqa: T201
        exit_cli_success(f"Rules context exported in {args.output_path}")
    except Exception as err:
        exit_cli_error(err)

#! python3  # noqa: E265

"""
    Sub-command in charge of running the main logic.

    Author: Julien M. (https://github.com/guts)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import argparse
import logging
from pathlib import Path

# submodules
from qgis_deployment_toolbelt.profiles.qdt_profile import QdtProfile
from qgis_deployment_toolbelt.utils.check_path import check_path

# #############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)


# ############################################################################
# ########## CLI #################
# ################################


def parser_extract_from_profile(
    subparser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """Set the argument parser for deployment subcommand.

    Args:
        subparser (argparse.ArgumentParser): parser to set up

    Returns:
        argparse.ArgumentParser: parser ready to use
    """
    subparser.add_argument(
        "-f",
        "--from",
        "--from-profile-path",
        dest="input_profile_path",
        help="Path to the QGIS profile to extract.",
        type=str,
    )

    subparser.add_argument(
        "-t",
        "--to",
        "--to-profile-path",
        dest="output_profile_path",
        help="Path where to store the QDT profile.",
        type=str,
    )

    subparser.set_defaults(func=run)

    return subparser


# ############################################################################
# ########## MAIN ################
# ################################


def run(args: argparse.Namespace):
    """Run the main logic.

    Args:
        args (argparse.Namespace): arguments passed to the subcommand
    """
    logger.debug(f"Running {args.command} with {args}")

    # check input profile exists
    check_path(
        input_path=args.input_profile_path,
        must_be_a_file=False,
        must_be_a_folder=True,
        must_be_readable=True,
        raise_error=True,
    )
    input_qgis_profile_path = Path(args.input_profile_path)

    # make sure output profile folder exists
    output_qdt_profile_path = Path(args.output_profile_path)
    output_qdt_profile_path.mkdir(parents=True, exist_ok=True)

    src_profile: QdtProfile = QdtProfile.from_profile_folder(
        input_profile_folder=input_qgis_profile_path
    )

    print(src_profile)

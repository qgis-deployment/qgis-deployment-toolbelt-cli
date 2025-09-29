#! python3  # noqa: E265
# Copyright 2023 Julien Moura (Oslandia)
# SPDX-License-Identifier: Apache-2.0

"""
Main command-line.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import argparse
import logging
import sys
from os import environ

# submodules
from qgis_deployment_toolbelt.__about__ import (
    __author__,
    __summary__,
    __title__,
    __title_clean__,
    __uri_homepage__,
    __version__,
    __version_clean__,
)
from qgis_deployment_toolbelt.commands.cmd_rules_context import (
    parser_rules_context_export,
)
from qgis_deployment_toolbelt.commands.deployment import parser_main_deployment
from qgis_deployment_toolbelt.commands.upgrade import parser_upgrade
from qgis_deployment_toolbelt.utils.journalizer import configure_logger


# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def add_common_arguments(
    parser_to_update: argparse.ArgumentParser,
    add_verbosity: bool = True,
    add_proxy: bool = True,
):
    """Apply common arguments to an existing parser.

    Args:
        parser_to_update (argparse.ArgumentParser): parser to which arguments need to be added
        add_verbosity (bool, optional): if enabled, add --verbose. Defaults to True.
        add_proxy (bool, optional): if enabled, adds --proxy-http. Defaults to True.

    Returns:
        argparse.ArgumentParser: parser with added options
    """
    if add_verbosity:
        parser_to_update.add_argument(
            "-v",
            "--verbose",
            action="count",
            default=1,
            dest="verbosity",
            help="Verbosity level. None = WARNING, -v = INFO, -vv = DEBUG. Can be set with "
            "QDT_LOGS_LEVEL environment variable and logs location with QDT_LOGS_DIR.",
        )

    if add_proxy:
        parser_to_update.add_argument(
            "--proxy-http",
            default=None,
            dest="proxy_http",
            help="Option to specify an HTTP proxy in the form: "
            "scheme://[user:passwd@]proxy.server:port",
            metavar="QDT_PROXY_HTTP",
            type=str,
        )

    return parser_to_update


def set_default_subparser(
    parser_to_update: argparse.ArgumentParser,
    default_subparser_name: str,
    args: list | None = None,
):
    """Set a default subparser to a parent parser. Call after setup and just before
        parse_args().
        See: <https://stackoverflow.com/questions/5176691/argparse-how-to-specify-a-default-subcommand>

    Args:
        parser_to_update (argparse.ArgumentParser): parent parser to add
        default_subparser_name (str): name of the subparser to call by default
        args (list, optional): if set is the argument list handed to parse_args().
        Defaults to None.
    """
    subparser_found = False
    for arg in sys.argv[1:]:
        if arg in [
            "-h",
            "--help",
            "--version",
            "--no-logfile",
        ]:  # ignore main parser args
            break

    else:
        for x in parser_to_update._subparsers._actions:
            if not isinstance(x, argparse._SubParsersAction):
                continue
            for sp_name in x._name_parser_map.keys():
                if sp_name in sys.argv[1:]:
                    subparser_found = True
        if not subparser_found:
            # insert default in first position, this implies no
            # global options without a sub_parsers specified
            if args is None:
                sys.argv.insert(1, default_subparser_name)
            else:
                args.insert(0, default_subparser_name)


# ############################################################################
# ########## MAIN ################
# ################################
def main(in_args: list[str] | None = None):
    """Main CLI entrypoint.

    Args:
        in_args (List[str], optional): list of command-line arguments. Defaults to None.
    """
    # create the top-level parser
    main_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Developed by: {__author__}\nDocumentation: {__uri_homepage__}",
        description=f"{__title__} {__version__} - {__summary__}",
        argument_default=argparse.SUPPRESS,
    )

    # -- ROOT ARGUMENTS --
    main_parser.add_argument(
        "--no-logfile",
        default=True,
        action="store_false",
        dest="opt_logfile_disabled",
        help="Disable log file. Log files are usually created, rotated and stored in the"
        "folder set by QDT_LOGS_DIR.",
    )

    main_parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Display CLI version",
    )

    add_common_arguments(main_parser, add_verbosity=True, add_proxy=True)
    # -- SUB-COMMANDS --
    subparsers = main_parser.add_subparsers(title="Sub-commands", dest="command")

    # Main logic
    subcmd_deployment = subparsers.add_parser(
        "deploy",
        help="QDT's main logic: run the deployment's scenario.",
        formatter_class=main_parser.formatter_class,
        prog="deployment",
    )
    add_common_arguments(subcmd_deployment)
    parser_main_deployment(subcmd_deployment)

    # Rules context
    subcmd_rules_context = subparsers.add_parser(
        "export-rules-context",
        help="Export QDT rules context taking into account the local environment to "
        "help rules writing.",
        formatter_class=main_parser.formatter_class,
        prog="rules-context-export",
    )
    add_common_arguments(subcmd_rules_context)
    parser_rules_context_export(subcmd_rules_context)

    # Upgrader
    subcmd_upgrade = subparsers.add_parser(
        "upgrade",
        aliases=["auto-update", "update"],
        help="Check if a new version of QDT is available and download it locally.",
        formatter_class=main_parser.formatter_class,
        prog="upgrade",
    )
    add_common_arguments(subcmd_upgrade)
    parser_upgrade(subcmd_upgrade)

    # -- PARSE ARGS --
    set_default_subparser(parser_to_update=main_parser, default_subparser_name="deploy")

    # just get passed args
    args = main_parser.parse_args(in_args)

    # proxy configuration
    if args.proxy_http:
        environ["QDT_PROXY_HTTP"] = args.proxy_http

    # log configuration
    if args.opt_logfile_disabled:
        configure_logger(
            verbosity=args.verbosity,
            logfile=f"{__title_clean__}_{__version_clean__}.log",
        )
    else:
        configure_logger(verbosity=args.verbosity)

    # add the handler to the root logger
    logger = logging.getLogger(__title_clean__)
    logger.debug(f"Log level set: {logging.getLevelName(args.verbosity)}")

    # -- RUN LOGIC --
    if hasattr(args, "func"):
        args.func(args)


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    # launch cli
    main()  # required by unittest

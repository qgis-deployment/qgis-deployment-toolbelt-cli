#! python3  # noqa: E265

"""
Microsoft Version Info templater.

See:

    - https://docs.microsoft.com/en-us/windows/win32/menurc/versioninfo-resource
    - https://docs.microsoft.com/en-us/windows/win32/api/verrsrc/ns-verrsrc-vs_fixedfileinfo
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import argparse
import sys
from os import W_OK, access, path
from pathlib import Path

# 3rd party
from packaging.version import parse as parse_version

sys.path.insert(0, path.abspath(r"."))

# module
from qgis_deployment_toolbelt import __about__

# #############################################################################
# ########### MAIN #################
# ##################################

# Parse the version using packaging.version which handles setuptools_scm formats
# This supports formats like:
# - Standard releases: "1.2.3"
# - Development versions: "1.2.3.dev4+g1234567"
# - Pre-releases: "1.2.3a1", "1.2.3b2", "1.2.3rc1"
try:
    parsed_version = parse_version(__about__.__version__)
    # Extract major, minor, patch from the parsed version
    # For development versions like "0.1.dev1+ge6f014e", this will give us (0, 1, 0)
    if hasattr(parsed_version, "release") and len(parsed_version.release) >= 3:
        semver = parsed_version.release[:3]  # (major, minor, patch)
    elif hasattr(parsed_version, "release") and len(parsed_version.release) == 2:
        # Handle case where only major.minor is provided
        semver = (*parsed_version.release, 0)  # (major, minor, 0)
    elif hasattr(parsed_version, "release") and len(parsed_version.release) == 1:
        # Handle case where only major is provided
        semver = (parsed_version.release[0], 0, 0)  # (major, 0, 0)
    else:
        # Fallback for unexpected formats
        semver = (0, 1, 0)
except Exception as e:
    raise ValueError(
        f"Invalid version format: {__about__.__version__}. "
        f"Error parsing version: {e}"
    )


REPLACEMENT_VALUES = {
    "[AUTHOR]": __about__.__author__,
    "[COPYRIGHT]": __about__.__copyright__,
    "[DESCRIPTION]": __about__.__summary__,
    "[EXECUTABLE_NAME]": __about__.__executable_name__,
    "[TITLE]": __about__.__title__,
    "[VERSION_INFO_TUPLE]": "({},{},{},0)".format(*semver),
    "[VERSION_SEMVER]": __about__.__version__,
}


def run():
    """Minimal CLI to generate a MS Version Info using a template and an about module.

    :raises FileNotFoundError: if input template is missing
    :raises PermissionError: if output file already exists but it's not writable
    :raises SystemExit: in case of user abort

    :example:

    .. code-block:: bash

        python version_info_templater.py
    """
    # variables
    script_path = Path(__file__).parent

    # cli parser arguments
    parser = argparse.ArgumentParser(
        epilog=(
            "The generated output is saved to a file to be used "
            "as the input for a version resource on any of the "
            "executable targets in an Installer spec file."
        )
    )
    parser.add_argument(
        "-t",
        "--template",
        default=str(script_path / "template_win_exe_version_info.txt"),
        help="Full pathname of a template file (.txt)",
        metavar="template",
        nargs=1,
        type=str,
    )
    parser.add_argument(
        "-o",
        "--out_filename",
        default="version_info.txt",
        help="Filename where the version info will be saved",
        metavar="out-filename",
        nargs=1,
        type=str,
    )

    args = parser.parse_args()

    try:
        # check input file
        in_template = Path(args.template)
        if not in_template.is_file():
            raise FileNotFoundError(in_template)

        # check output file
        out_version_file = Path(args.out_filename)
        if out_version_file.exists() and not access(out_version_file, W_OK):
            raise PermissionError(out_version_file.resolve())

        # read template
        template_txt = in_template.read_text()

        # replace values in template
        for val, repl in REPLACEMENT_VALUES.items():
            template_txt = template_txt.replace(val, str(repl))

        # write new file
        out_version_file.write_text(template_txt, encoding="UTF8")

        # log user
        print(f"Version info written to: {out_version_file.resolve()}")
    except KeyboardInterrupt:
        raise SystemExit("Aborted by user request.")


# Stand alone execution
if __name__ == "__main__":
    run()

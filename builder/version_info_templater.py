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
import re
import sys
from os import W_OK, access
from pathlib import Path


sys.path.insert(0, Path().resolve().as_posix())

# module
from qgis_deployment_toolbelt import __about__


# #############################################################################
# ########### MAIN #################
# ##################################

# Define a regular expression pattern to match the version string
pattern = re.compile(r"(\d+)\.(\d+)\.(\d+)")
semver = pattern.match(__about__.__version__).groups()


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
    except KeyboardInterrupt as err:
        raise SystemExit("Aborted by user request.") from err


# Stand alone execution
if __name__ == "__main__":
    run()

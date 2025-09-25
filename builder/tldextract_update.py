#! python3  # noqa: E265

"""
Create tldextract update cache folder

"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import argparse
import urllib.request
from os import W_OK, access
from pathlib import Path

# 3rd party
from tldextract import TLDExtract


# #############################################################################
# ########### MAIN #################
# ##################################


def run():
    """Minimal CLI to generate a tldextract cache.

    :raises PermissionError: if output directory already exists but it's not writable
    :raises SystemExit: in case of user abort

    :example:

    .. code-block:: bash

        python tldextract_update.py
    """
    # variables
    script_path = Path(__file__).parent

    # cli parser arguments
    parser = argparse.ArgumentParser(epilog=("tdlextract cache are created in output folder"))
    parser.add_argument(
        "-o",
        "--output",
        default=script_path / "build" / "tldextract_cache",
        help="tld extract cache output folder",
        type=Path,
    )

    args = parser.parse_args()

    try:
        # check output directory
        output_dir = Path(args.output)
        if output_dir.exists() and not access(output_dir, W_OK):
            raise PermissionError(output_dir.resolve())

        output_dir.mkdir(exist_ok=True, parents=True)

        tld_extract = TLDExtract(str(output_dir / ".suffix_cache"))
        tld_extract.update(True)

        urllib.request.urlretrieve(
            "https://publicsuffix.org/list/public_suffix_list.dat",
            output_dir / ".tld_set_snapshot",
        )

        # log user
        print(f"tldextract cache written to: {output_dir.resolve()}")
    except KeyboardInterrupt:
        raise SystemExit("Aborted by user request.") from None


# Stand alone execution
if __name__ == "__main__":
    run()

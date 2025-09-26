#! python3  # noqa: E265

"""Convert PNGF file(s) to multisizes ico.

Widely inspired from:

- png2ico (https://github.com/dbconfig/png2ico), MIT
- PyInstaller (https://github.com/pyinstaller/pyinstaller/blob/c7ff86f871d064110452562ed87c4fb95d2a718e/PyInstaller/building/icon.py), GPL2 or later
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import logging
from pathlib import Path


# 3rd party
try:
    from PIL import Image, UnidentifiedImageError
except ImportError as error:
    import sys

    sys.exit(
        f"Please install Pillow ('pip install pillow') to make image conversion. Trace: {error}"
    )

# package
from qgis_deployment_toolbelt.utils.check_path import check_path


# #############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

AUTO_RESIZE_OUTPUT_ICO_SIZES: tuple[tuple[int, int], ...] = (
    (16, 16),
    (24, 24),
    (32, 32),
    (48, 48),
    (64, 64),
    (128, 128),
    (255, 255),
)


# #############################################################################
# ########## Functions #############
# ##################################


def png2ico(in_png_path: Path, out_ico_path: Path | None = None) -> Path:
    """Convert a PNG file to an multisize ICO.

    Args:
        in_png_path (Path): input PNG image file path.
        out_ico_path (Path | None): output ico file path, optional.

    Raises:
        error: if input file does not exist or something goes wrong during conversion.

    Returns:
        Path: output ico file path
    """
    # check if input file exists
    check_path(
        input_path=in_png_path,
        must_be_a_file=True,
        must_be_a_folder=False,
        must_be_readable=True,
        must_exists=True,
    )

    # output path
    if not isinstance(out_ico_path, Path):
        out_ico_path = in_png_path.with_suffix(".ico")

    try:
        with Image.open(in_png_path) as im:
            # If an image uses a custom palette + transparency, convert it to RGBA for a
            # better alpha mask depth.
            if im.mode == "P" and im.info.get("transparency", None) is not None:
                # The bit depth of the alpha channel will be higher, and the images will
                # look better when eventually scaled to multiple sizes (16,24,32,..) for
                # the ICO format for example.
                im = im.convert("RGBA")
            im.save(out_ico_path, sizes=AUTO_RESIZE_OUTPUT_ICO_SIZES)
    except UnidentifiedImageError as error:
        logger.error(
            f"Something went wrong converting icon image '{in_png_path}' to .ico with Pillow,"
        )
        raise error

    return out_ico_path


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    pass

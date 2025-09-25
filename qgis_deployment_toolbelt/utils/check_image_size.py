#! python3  # noqa: E265

"""
Check image size using pure Python <https://github.com/shibukawa/imagesize_py>.

Author: Julien Moura (https://github.com/guts)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
import xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path

# 3rd party
import imagesize


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Functions #############
# ##################################


def get_image_size(image_filepath: Path) -> tuple[int, int] | None:
    """Get image dimensions as a tuple (width,height). Return None in case of error.

    :param Path image_filepath: path to the image

    :return Tuple[int, int]: dimensions tuple (width,height)
    """
    # handle SVG
    if image_filepath.suffix.lower() == ".svg":
        svg_size = get_svg_size(image_filepath)
        if not svg_size:
            return None
        else:
            return svg_size

    # get image dimensions
    try:
        return imagesize.get(image_filepath)
    except ValueError as exc:
        logger.error(f"Invalid image: {image_filepath.resolve()}. Trace: {exc}")
    except Exception as exc:
        logger.error(
            f"Something went wrong reading the image: {image_filepath.resolve()}. Trace: {exc}"
        )

    return None


def get_svg_size(image_filepath: Path) -> tuple[int, int] | None:
    """Extract SVG width and height from a SVG file and convert them into integers. \
    Relevant and working only if the file root has width and height attributes.

    :param Path image_filepath: path to the svg file

    :return Tuple[int, int]: tuple of dimensions as integers (width,height)
    """
    try:
        tree = ET.parse(image_filepath)  # noqa: S314
        root = tree.getroot()
    except Exception as err:
        logger.error(f"Unable to open SVG file as XML: {image_filepath}. Trace: {err}")
        return None

    try:
        return int(Decimal(root.attrib["width"])), int(Decimal(root.attrib["height"]))
    except Exception as err:
        logger.warning(
            "Unable to determine image dimensions from width/height "
            f"attributes: {image_filepath}. It migh be infinitely scalable. Trace: {err}"
        )
        return None


def check_image_dimensions(
    image_filepath: Path,
    min_width: int = 500,
    max_width: int = 600,
    min_height: int = 250,
    max_height: int = 350,
    allowed_images_extensions: tuple = (".jpg", ".jpeg", ".png", ".svg"),
) -> bool | None:
    """Check input image dimensions against passed limits.

    :param Path image_filepath: path to the image to check
    :param int min_width: minimum width, defaults to 500
    :param int max_width: maximum width, defaults to 600
    :param int min_height: minimum height, defaults to 250
    :param int max_height: maximum height, defaults to 350

    :return bool: True if image dimensions are inferior
    """

    if image_filepath.suffix.lower() not in allowed_images_extensions:
        logger.error(
            f"Image extension {image_filepath.suffix.lower()} is not one of "
            f"supported: {allowed_images_extensions}"
        )
        return None

    image_dimensions = get_image_size(image_filepath=image_filepath)
    if not image_dimensions:
        logger.info(
            f"Unable to determine image dimensions ({image_filepath.resolve()}), "
            "so unable to check it it complies with limits."
        )
        return None

    return all(
        dim <= limit
        for dim, limit in zip(image_dimensions, (max_width, max_height), strict=False)
    )

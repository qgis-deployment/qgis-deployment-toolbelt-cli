#! python3  # noqa: E265

"""Convert PNGF file(s) to multisizes ico. And vice-versa. Requires pillow (PIL).

Widely inspired from:

- png2ico (https://github.com/dbconfig/png2ico), MIT
- PyInstaller (https://github.com/pyinstaller/pyinstaller/blob/c7ff86f871d064110452562ed87c4fb95d2a718e/PyInstaller/building/icon.py), GPL2 or later
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import argparse
import logging
import sys
from pathlib import Path

# 3rd party
from PIL import Image, UnidentifiedImageError


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


def ico2png(
    in_ico_path: Path, out_png_path: Path | None = None, size: int = 256
) -> Path:
    """Convert an ICO file to PNG, picking the best available resolution.

    Args:
        in_ico_path (Path): input ICO image file path.
        out_png_path (Path | None): output PNG file path, optional. Defaults to
            same location as input with .png extension.
        size (int): target size (width and height) in pixels. The largest
            available size in the ICO up to this value will be used.
            Defaults to 256.

    Raises:
        UnidentifiedImageError: if Pillow cannot open the input file.

    Returns:
        Path: output PNG file path.
    """

    if not isinstance(out_png_path, Path):
        out_png_path = in_ico_path.with_suffix(".png")

    try:
        with Image.open(in_ico_path) as im:
            # ICO files can embed multiple sizes; pick the largest one <= target size
            if hasattr(im, "ico"):
                available_sizes = im.ico.sizes()
                best = max(
                    (s for s in available_sizes if s[0] <= size),
                    default=max(available_sizes),
                )
                im.size = best
                im.load()

            if im.mode != "RGBA":
                im = im.convert("RGBA")

            im.save(out_png_path, format="PNG")
    except UnidentifiedImageError as error:
        logger.exception(
            f"Something went wrong converting icon image '{in_ico_path}' to .png with Pillow."
        )
        raise error

    logger.debug(f"Converted ICO to PNG: {in_ico_path} -> {out_png_path}")
    return out_png_path


def png2ico(in_png_path: Path, out_ico_path: Path | None = None) -> Path:
    """Convert a PNG file to an multisize ICO.

    Args:
        in_png_path (Path): input PNG image file path.
        out_ico_path (Path | None): output ico file path, optional.

    Raises:
        UnidentifiedImageError: if input file does not exist or something goes wrong during conversion.

    Returns:
        Path: output ico file path
    """

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
        logger.exception(
            f"Something went wrong converting icon image '{in_png_path}' to .ico with Pillow,"
        )
        raise error

    return out_ico_path


# #############################################################################
# ########## CLI ###################
# ##################################


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert between ICO and PNG formats.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  icon_converter.py ico2png input.ico
  icon_converter.py ico2png input.ico --output output.png --size 128
  icon_converter.py png2ico input.png --output output.ico""",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: ico2png
    ico2png_parser = subparsers.add_parser("ico2png", help="Convert ICO to PNG.")
    ico2png_parser.add_argument(
        "input",
        type=Path,
        help="Input ICO file path.",
    )
    ico2png_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output PNG file path (default: same as input with .png extension).",
    )
    ico2png_parser.add_argument(
        "-s",
        "--size",
        type=int,
        default=256,
        help="Target size in pixels (default: 256).",
    )

    # Subcommand: png2ico
    png2ico_parser = subparsers.add_parser("png2ico", help="Convert PNG to ICO.")
    png2ico_parser.add_argument(
        "input",
        type=Path,
        help="Input PNG file path.",
    )
    png2ico_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output ICO file path (default: same as input with .ico extension).",
    )

    return parser.parse_args()


def main() -> int:
    """Entry point for the CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    args = parse_args()

    try:
        if args.command == "ico2png":
            output_path = ico2png(args.input, args.output, args.size)
            print(f"Converted {args.input} to {output_path}")
        elif args.command == "png2ico":
            output_path = png2ico(args.input, args.output)
            print(f"Converted {args.input} to {output_path}")
    except UnidentifiedImageError as e:
        logger.error(f"Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_utils_images_size
    # for specific test
    python -m unittest tests.test_utils_images_size.TestUtilsImagesSizeChecker.get_svg_size
"""

# standard library
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

# 3rd party
from PIL import Image

# project
from qgis_deployment_toolbelt.__about__ import __title_clean__, __version__
from qgis_deployment_toolbelt.utils.check_image_size import (
    check_image_dimensions,
    get_image_size,
)


# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsImagesSizeChecker(unittest.TestCase):
    """Test package utilities."""

    # -- Standard methods --------------------------------------------------------
    @classmethod
    def setUpClass(cls) -> None:
        """Set up test."""

        cls.img_tmp_folder = TemporaryDirectory(
            prefix=f"{__title_clean__}_{__version__}_"
        )

        # create a temporary image
        cls.img_black_800x600 = Path(cls.img_tmp_folder.name, "img_black_800x600.jpg")
        width = 800
        height = 600
        image = Image.new("RGB", (width, height), "black")
        image.save(cls.img_black_800x600)

    @classmethod
    def tearDownClass(cls):
        """Executed after each test."""
        cls.img_tmp_folder.cleanup()

    # -- TESTS ---------------------------------------------------------
    def test_svg_size_with_dimensions(self):
        """Test svg size retriever."""
        svg_with_dimensions_attributes = Path(
            "tests/fixtures/miscellaneous/sample_with_dimensions_attributes.svg"
        )

        self.assertTrue(svg_with_dimensions_attributes.is_file())
        # svg with dimensions set
        svg_size = get_image_size(image_filepath=svg_with_dimensions_attributes)

        self.assertIsInstance(svg_size, tuple)
        self.assertIsInstance(svg_size[0], int)
        self.assertIsInstance(svg_size[1], int)
        self.assertEqual(svg_size[0], 853)
        self.assertEqual(svg_size[1], 568)

    def test_svg_size_without_dimensions(self):
        """Test svg size retriever."""
        svg_without_dimensions_attributes = Path(
            "tests/fixtures/miscellaneous/sample_without_dimensions_attributes.svg"
        )
        self.assertTrue(svg_without_dimensions_attributes.is_file())
        svg_size = get_image_size(image_filepath=svg_without_dimensions_attributes)

        self.assertIsNone(svg_size)

    def test_get_image_dimensions(self):
        img_800x600 = get_image_size(self.img_black_800x600)
        self.assertIsInstance(img_800x600, tuple)
        self.assertEqual(img_800x600[0], 800)
        self.assertEqual(img_800x600[1], 600)

    def test_check_image_dimensions(self):
        """Test image dimensions checker."""
        self.assertTrue(
            check_image_dimensions(
                image_filepath=self.img_black_800x600, max_width=801, max_height=601
            )
        )

        self.assertFalse(
            check_image_dimensions(
                image_filepath=self.img_black_800x600, max_width=300, max_height=601
            )
        )

        self.assertFalse(
            check_image_dimensions(
                image_filepath=self.img_black_800x600, max_width=2000, max_height=200
            )
        )

        self.assertFalse(
            check_image_dimensions(
                image_filepath=self.img_black_800x600, max_width=300, max_height=500
            )
        )

        self.assertFalse(
            check_image_dimensions(
                image_filepath=self.img_black_800x600,
                max_width=300,
                max_height=500,
                allowed_images_extensions=(".png", ".webp"),
            )
        )


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

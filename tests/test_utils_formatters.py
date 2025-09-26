#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_utils_formatters
    # for specific test
    python -m unittest tests.test_utils_formatters.TestUtilsFormatters.test_convert_octets
"""

# standard library
import unittest

# project
from qgis_deployment_toolbelt.utils.formatters import (
    convert_octets,
    url_ensure_trailing_slash,
)


# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsFormatters(unittest.TestCase):
    """Test package utilities."""

    def test_convert_octets(self):
        """Test file size formatter."""
        self.assertEqual(
            convert_octets(1024),
            "1.0 Ko",
        )

        self.assertEqual(
            convert_octets(2097152),
            "2.0 Mo",
        )

    def test_url_ensure_trailing_slash(self):
        """Test URL trailing slash."""
        self.assertEqual(
            url_ensure_trailing_slash(
                in_url="https://qgis-deployment.github.io/qgis-deployment-toolbelt-cli"
            ),
            "https://qgis-deployment.github.io/qgis-deployment-toolbelt-cli/",
        )

        self.assertEqual(
            url_ensure_trailing_slash(
                in_url="https://qgis-deployment.github.io/qgis-deployment-toolbelt-cli/"
            ),
            "https://qgis-deployment.github.io/qgis-deployment-toolbelt-cli/",
        )


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

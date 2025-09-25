#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_utils_url_helpers
    # for specific test
    python -m unittest tests.test_utils_url_helpers.TestUtilsUrlHelpers.test_check_str_is_url
"""

# standard library
import unittest
from pathlib import Path

# project
from qgis_deployment_toolbelt.__about__ import __uri__
from qgis_deployment_toolbelt.utils.url_helpers import check_str_is_url


# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsUrlHelpers(unittest.TestCase):
    """Test URL helpers."""

    def test_check_str_is_url(self):
        """Test function that determines if a str or Path is a valid URL."""
        self.assertTrue(check_str_is_url(input_str=__uri__))
        self.assertTrue(
            check_str_is_url(input_str="ftp://fakeftp:21", ref_shemes=("ftp", "http")),
        )
        self.assertFalse(check_str_is_url(input_str=Path(__uri__), raise_error=False))
        self.assertFalse(check_str_is_url(input_str=Path(__file__), raise_error=False))

        with self.assertRaises((TypeError, ValueError)):
            check_str_is_url(input_str=Path(__file__), raise_error=True)


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

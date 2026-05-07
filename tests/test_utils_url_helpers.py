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
from qgis_deployment_toolbelt.utils.url_helpers import (
    check_str_is_url,
    filename_from_url,
)


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

    def test_url_basic(self):
        """Test basic url to filename."""
        url = "https://qdt.com/files/data.txt"
        self.assertEqual(filename_from_url(url), "qdtcom/files/data.txt")

    def test_url_file_at_root(self):
        """Test url with file at root."""
        url = "https://github.com/data.txt"
        self.assertEqual(filename_from_url(url), "githubcom/data.txt")

    def test_url_nested_path(self):
        """Test url with subdomain."""
        url = "https://sub.oslandia.com/a/b/c/file.zip"
        self.assertEqual(filename_from_url(url), "suboslandiacom/abc/file.zip")

    def test_url_accents_and_spaces(self):
        """Test url with special chars, keeping them in filename."""
        url = "https://mälmo.com/dossier été/fîlé nâmé.txt"
        self.assertEqual(filename_from_url(url), "malmocom/dossier-ete/fîlé nâmé.txt")

    def test_url_query_string(self):
        """Test cleaning query rom url."""
        url = "https://example.com/files/data.txt?token=123"
        self.assertEqual(filename_from_url(url), "examplecom/files/data.txt")


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

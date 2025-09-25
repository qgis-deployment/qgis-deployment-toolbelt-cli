#! python3  # noqa E265

"""Usage from the repo root folder:

.. code-block:: python

    # for whole test
    python -m unittest tests.test_tree_qdt-files_json
    # for specific
    python -m unittest tests.test_tree_qdt-files_json.TestTreeQdtFilesReader.test_load_tree_json_files
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import json
import unittest
from pathlib import Path

# module target
from qgis_deployment_toolbelt.utils.tree_files_reader import tree_to_download_list


# #############################################################################
# ########## Classes ###############
# ##################################


class TestTreeQdtFilesReader(unittest.TestCase):
    """Test module."""

    # -- Standard methods --
    @classmethod
    def setUpClass(cls):
        """Executed when module is loaded before any test."""
        cls.tree_qdt_files = sorted(
            Path("tests/fixtures/").glob("treefiles/qdt-files*.json")
        )

    # -- Tests methods --
    def test_load_tree_json_files(self):
        """Test tree files loading and parsing."""
        self.assertGreaterEqual(len(self.tree_qdt_files), 1)
        for tree_file in self.tree_qdt_files:
            print(f"Processing {tree_file}")

            with tree_file.open(mode="r", encoding="utf-8") as in_json:
                tree_data = json.load(in_json)

            li_files_to_download = tree_to_download_list(tree_array=tree_data)
            # check type
            self.assertIsInstance(li_files_to_download, list)
            self.assertTrue(all([isinstance(f, str) for f in li_files_to_download]))

#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_utils_ini_custom_parser
    # for specific test
    python -m unittest tests.test_utils_ini_custom_parser.TestCustomConfigParser.test_file_path_storing
"""

# standard
import unittest
from pathlib import Path

# project
from qgis_deployment_toolbelt.utils.ini_parser_with_path import CustomConfigParser


# ############################################################################
# ########## Classes #############
# ################################


class TestCustomConfigParser(unittest.TestCase):
    """Test extended ConfigParser that store the initial ini file pathmodule."""

    def test_file_path_storing(self):
        # temporary file
        test_file_path = Path("tests/fixtures/tmp/test_custom_config_parser.ini")
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        test_file_path.write_text("[Section1]\noption1 = value1\n")

        # read and get back the initial file path
        parser = CustomConfigParser()
        parser.read(test_file_path)

        self.assertEqual(parser.get_initial_file_path(), test_file_path)

        # clean up
        test_file_path.unlink()


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

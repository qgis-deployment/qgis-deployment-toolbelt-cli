#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_utils
    # for specific test
    python -m unittest tests.test_utils.TestUtilsWin32.test_win32_getenv
"""

# standard library
import unittest
from sys import platform as opersys

# project
from qgis_deployment_toolbelt.utils.win32utils import get_environment_variable


# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsWin32(unittest.TestCase):
    """Test package utilities."""

    @unittest.skipIf(opersys != "win32", "Test specific to Windows.")
    def test_win32_getenv(self):
        """Test specific Windows environment variable getter."""
        # OK
        self.assertIsInstance(get_environment_variable("TEMP"), str)

        # KO
        self.assertIsNone(get_environment_variable("YOUPI"))


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

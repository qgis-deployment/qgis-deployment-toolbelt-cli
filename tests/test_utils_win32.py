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


# Imports depending on operating system
if opersys == "win32":
    """windows"""
    # standard
    import winreg

# project
from qgis_deployment_toolbelt.utils.win32utils import (
    get_environment_variable,
    read_registry_value,
)


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

    @unittest.skipUnless(opersys == "win32", "Test specific to Windows.")
    def test_win32_read_registry_value(self):
        """Test specific Windows registry value reader."""
        # OK
        self.assertIsInstance(
            read_registry_value(
                (
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
                ),
                "ProductName",
            ),
            str,
        )

        # KO
        self.assertIsNone(
            read_registry_value(
                (
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Explorer",
                ),
                "NonExistentKey",
            )
        )


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

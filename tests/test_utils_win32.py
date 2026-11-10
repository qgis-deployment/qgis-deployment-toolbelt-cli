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
import logging
import unittest
from sys import platform as opersys
from unittest.mock import MagicMock, patch

# project
from qgis_deployment_toolbelt.utils import os_windows
from qgis_deployment_toolbelt.utils.os_router import get_environment_variable


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


class TestUtilsWin32MissingEnvVar(unittest.TestCase):
    """Test registry helpers with a mocked `winreg` (runs on any OS)."""

    def setUp(self) -> None:
        """Mock the registry module so that every variable is missing."""
        winreg = MagicMock()
        winreg.OpenKey.return_value.__enter__.return_value = "key"
        winreg.QueryValueEx.side_effect = FileNotFoundError
        winreg.DeleteValue.side_effect = FileNotFoundError
        self.winreg = winreg
        for name, value in (
            ("winreg", winreg),
            ("user_hkey", ("HKCU", "Environment")),
            ("system_hkey", ("HKLM", "Environment")),
        ):
            patcher = patch.object(os_windows, name, value, create=True)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_delete_missing_does_not_log_error(self) -> None:
        """Deleting a missing variable is silent above DEBUG (issue #938)."""
        with self.assertNoLogs(os_windows.logger, level=logging.INFO):
            self.assertFalse(os_windows.delete_environment_variable("MISSING"))
        self.winreg.DeleteValue.assert_not_called()

    def test_access_denied_still_logs_error(self) -> None:
        """Registry errors other than 'missing' are never downgraded."""
        self.winreg.QueryValueEx.side_effect = PermissionError
        with self.assertLogs(os_windows.logger, level=logging.ERROR):
            self.assertFalse(os_windows.delete_environment_variable("DENIED"))


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

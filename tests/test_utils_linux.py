#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_utils
    # for specific test
    python -m unittest tests.test_utils.TestUtilsLinux.test_win32_getenv
"""

# standard library
import tempfile
import unittest
from os import environ
from pathlib import Path
from sys import platform as opersys
from unittest.mock import patch

# project
from qgis_deployment_toolbelt.utils import os_linux


# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsLinux(unittest.TestCase):
    """Test package utilities."""

    @unittest.skipIf(opersys != "linux", "Test specific to Linux.")
    def test_file_to_use_for_storing_environment_variables(self):
        """Test file priority in bash context."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_linux_utils_bash_profile"
        ) as tmp_dir_name:
            # reference fake bash files
            tmp_fake_dot_profile = Path(tmp_dir_name).joinpath(".profile")
            os_linux.bash_user_dot_profile = tmp_fake_dot_profile
            tmp_fake_dot_bash_login = Path(tmp_dir_name).joinpath(".bash_login")
            os_linux.bash_user_dot_bash_login = tmp_fake_dot_bash_login
            tmp_fake_dot_bash_profile = Path(tmp_dir_name).joinpath(".bash_profile")
            os_linux.bash_user_dot_bash_profile = tmp_fake_dot_bash_profile

            # create fake .profile
            tmp_fake_dot_profile.touch()
            self.assertEqual(
                os_linux.bash_user_which_file_to_store(),
                tmp_fake_dot_profile,
            )

            # create fake .bash_login
            tmp_fake_dot_bash_login.touch()
            self.assertEqual(
                os_linux.bash_user_which_file_to_store(),
                tmp_fake_dot_bash_login,
            )

            # create fake bash_profile
            tmp_fake_dot_bash_profile.touch()
            os_linux.bash_user_dot_bash_profile = Path(tmp_dir_name).joinpath(
                ".bash_profile"
            )
            self.assertEqual(
                os_linux.bash_user_which_file_to_store(),
                tmp_fake_dot_bash_profile,
            )

    def test_get_xdg_data_home(self):
        """Use XDG_DATA_HOME used only it's an absolute path."""
        default = Path.home() / ".local/share"
        with patch.dict(environ, clear=False) as patched_environ:
            patched_environ.pop("XDG_DATA_HOME", None)
            self.assertEqual(os_linux.get_xdg_data_home(), default)

        absolute = Path.home() / "xdg_data"
        for value, expected in (("", default), (str(absolute), absolute)):
            with (
                self.subTest(value=value),
                patch.dict(environ, {"XDG_DATA_HOME": value}),
            ):
                self.assertEqual(os_linux.get_xdg_data_home(), expected)

        with (
            patch.dict(environ, {"XDG_DATA_HOME": "relative/xdg_data"}),
            self.assertLogs("qgis_deployment_toolbelt.utils.os_linux", level="DEBUG"),
        ):
            self.assertEqual(os_linux.get_xdg_data_home(), default)


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

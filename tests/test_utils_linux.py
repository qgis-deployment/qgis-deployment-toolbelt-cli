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
from pathlib import Path
from sys import platform as opersys

# project
from qgis_deployment_toolbelt.utils import linux_utils


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
            linux_utils.bash_user_dot_profile = tmp_fake_dot_profile
            tmp_fake_dot_bash_login = Path(tmp_dir_name).joinpath(".bash_login")
            linux_utils.bash_user_dot_bash_login = tmp_fake_dot_bash_login
            tmp_fake_dot_bash_profile = Path(tmp_dir_name).joinpath(".bash_profile")
            linux_utils.bash_user_dot_bash_profile = tmp_fake_dot_bash_profile

            # create fake .profile
            tmp_fake_dot_profile.touch()
            self.assertEqual(
                linux_utils.bash_user_which_file_to_store(),
                tmp_fake_dot_profile,
            )

            # create fake .bash_login
            tmp_fake_dot_bash_login.touch()
            self.assertEqual(
                linux_utils.bash_user_which_file_to_store(),
                tmp_fake_dot_bash_login,
            )

            # create fake bash_profile
            tmp_fake_dot_bash_profile.touch()
            linux_utils.bash_user_dot_bash_profile = Path(tmp_dir_name).joinpath(
                ".bash_profile"
            )
            self.assertEqual(
                linux_utils.bash_user_which_file_to_store(),
                tmp_fake_dot_bash_profile,
            )


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

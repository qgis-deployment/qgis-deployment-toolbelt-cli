#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_user_groups
    # for specific test
    python -m unittest tests.test_user_groups.TestUtilsUserGroups.test_win32_getenv
"""

# standard library
import unittest
from getpass import getuser
from sys import platform as opersys

# project
from qgis_deployment_toolbelt.utils.user_groups import (
    _is_computer_in_domain_powershell,
    _is_computer_in_domain_pyad,
    _is_computer_in_domain_win32,
    get_user_local_groups,
    is_computer_attached_to_a_domain,
    is_user_in_group,
)


# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsUserGroups(unittest.TestCase):
    """Test package utilities."""

    def test_computer_attached_to_domain(self):
        """Test if the computer belongs to a domain."""
        # for now, domain link is only supported on Windows
        if opersys != "win32":
            self.assertFalse(is_computer_attached_to_a_domain())
            return

        # test different methods on Windows but for now, no domain mocked in tests
        # TODO: mock domain link
        domain_status = is_computer_attached_to_a_domain()
        self.assertIsInstance(domain_status, bool)

        self.assertEqual(domain_status, _is_computer_in_domain_powershell())
        self.assertEqual(domain_status, _is_computer_in_domain_pyad())
        self.assertEqual(domain_status, _is_computer_in_domain_win32())

    def test_user_in_group(self):
        """Test function determining user's groups."""
        user_groups = get_user_local_groups()

        # test with existing group
        self.assertTrue(is_user_in_group(user_groups[0]))

        # test with unisting group
        self.assertFalse(is_user_in_group(group_name="fake_group", user_name=getuser()))


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

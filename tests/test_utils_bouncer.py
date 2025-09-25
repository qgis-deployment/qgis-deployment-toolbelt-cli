#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_utils_bouncer
    # for specific test
    python -m unittest tests.test_utils_bouncer.TestUtilsBouncer.test_bouncer_error
"""

# standard library
import unittest

# project
from qgis_deployment_toolbelt.utils.bouncer import (
    exit_cli_error,
    exit_cli_normal,
    exit_cli_success,
)


# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsBouncer(unittest.TestCase):
    """Test package utilities."""

    def test_bouncer_error(self):
        """Test bouncer error."""
        # test with simple string
        error_message = "fake error"

        with self.assertRaises(SystemExit) as err:
            exit_cli_error(error_message)
        exception = err.exception
        self.assertEqual(exception.code, error_message)

        self.assertIsNone(exit_cli_error(error_message, abort=False))

        # test with an Exception
        error = TypeError("fake type error")
        with self.assertRaises(SystemExit):
            exit_cli_error(error)
        self.assertIsNone(exit_cli_error(error, abort=False))

    def test_bouncer_normal(self):
        """Test bouncer normal."""
        # test with simple string
        error_message = "fake error"

        with self.assertRaises(SystemExit) as err:
            exit_cli_normal(error_message)
        exception = err.exception
        self.assertEqual(exception.code, 0)

        self.assertIsNone(exit_cli_normal(error_message, abort=False))

    def test_bouncer_success(self):
        """Test bouncer success."""
        # test with simple string
        error_message = "fake error"

        with self.assertRaises(SystemExit) as err:
            exit_cli_success(error_message)
        exception = err.exception
        self.assertEqual(exception.code, 0)

        self.assertIsNone(exit_cli_success(error_message, abort=False))


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

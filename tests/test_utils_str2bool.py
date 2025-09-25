#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_utils_str2bool
    # for specific test
    python -m unittest tests.test_utils_str2bool.TestUtilsStrToBool.test_str2bool
"""

# standard library
import unittest

# project
from qgis_deployment_toolbelt.utils.str2bool import str2bool


# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsStrToBool(unittest.TestCase):
    """Test package utilities."""

    def test_str2bool(self):
        """Test str2bool."""
        # OK
        self.assertTrue(str2bool("True"))
        self.assertTrue(str2bool(True))
        self.assertFalse(str2bool("False", raise_exc=True))
        self.assertIsNone(str2bool("faux", raise_exc=False))

        # KO
        with self.assertRaises(TypeError):
            str2bool(input_var=int(10), raise_exc=True)
        self.assertIsNone(str2bool(input_var=int(10), raise_exc=False))

        with self.assertRaises(ValueError):
            str2bool(input_var="vrai", raise_exc=True)


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

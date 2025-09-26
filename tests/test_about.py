#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_about
    # for specific test
    python -m unittest tests.test_about.TestAbout.test_version_semver
"""

# standard library
import unittest

# 3rd party
from packaging.version import parse
from validators import url

# project
from qgis_deployment_toolbelt import __about__


# ############################################################################
# ########## Classes #############
# ################################


class TestAbout(unittest.TestCase):
    """Test package metadata."""

    def test_metadata_types(self):
        """Test types."""
        # general
        self.assertIsInstance(__about__.__author__, str)
        self.assertIsInstance(__about__.__copyright__, str)
        self.assertIsInstance(__about__.__executable_name__, str)
        self.assertIsInstance(__about__.__package_name__, str)
        self.assertIsInstance(__about__.__license__, str)
        self.assertIsInstance(__about__.__summary__, str)
        self.assertIsInstance(__about__.__title__, str)
        self.assertIsInstance(__about__.__title_clean__, str)
        self.assertIsInstance(__about__.__uri_homepage__, str)
        self.assertIsInstance(__about__.__uri_repository__, str)
        self.assertIsInstance(__about__.__uri__, str)
        self.assertIsInstance(__about__.__version__, str)
        self.assertIsInstance(__about__.__version_info__, tuple)

        # misc
        self.assertLessEqual(len(__about__.__title_clean__), len(__about__.__title__))

        # urls
        self.assertTrue(url(__about__.__uri_homepage__))
        self.assertTrue(url(__about__.__uri_repository__))
        self.assertTrue(url(__about__.__uri__))

    def test_version_semver(self):
        """Test if version comply with semantic versioning."""
        self.assertTrue(parse(__about__.__version__))


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

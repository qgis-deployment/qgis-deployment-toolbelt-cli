#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_utils_slugifier
    # for specific test
    python -m unittest tests.test_utils_slugifier.TestUtilsSlugify.test_slugger
"""

# standard library
import unittest

# project
from qgis_deployment_toolbelt.utils.slugger import sluggy


# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsSlugify(unittest.TestCase):
    """Test package utilities."""

    def test_slugger(self):
        """Test minimalist slugify function."""
        # hyphen by default
        self.assertEqual(
            sluggy("Oyé oyé brâves gens de 1973 ! Hé oh ! Sentons-nous l'ail %$*§ ?!"),
            "oye-oye-braves-gens-de-1973-he-oh-sentons-nous-lail",
        )

        # with underscore
        self.assertEqual(
            sluggy("Nín hǎo. Wǒ shì zhōng guó rén", "_"),
            "nin_hao_wo_shi_zhong_guo_ren",
        )


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

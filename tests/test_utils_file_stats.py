#! python3  # noqa E265

"""
    Usage from the repo root folder:

    .. code-block:: bash
        # for whole tests
        python -m unittest tests.test_utils_file_stats
        # for specific test
        python -m unittest tests.test_utils_file_stats.TestUtilsFileStats.test_created_file_is_not_expired
"""


# standard library
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep

# project
from qgis_deployment_toolbelt.__about__ import __title_clean__, __version__
from qgis_deployment_toolbelt.utils.file_stats import is_file_older_than

# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsFileStats(unittest.TestCase):
    """Test package metadata."""

    def test_created_file_is_not_expired(self):
        """Test file creation 'age' is OK."""
        with TemporaryDirectory(
            f"{__title_clean__}_{__version__}_not_expired_"
        ) as tempo_dir:
            tempo_file = Path(tempo_dir, "really_recent_file.txt")
            tempo_file.touch()
            sleep(3)
            self.assertFalse(is_file_older_than(Path(tempo_file)))

    def test_created_file_has_expired(self):
        """Test file creation 'age' is too old."""
        with TemporaryDirectory(
            prefix=f"{__title_clean__}_{__version__}_expired_"
        ) as tempo_dir:
            tempo_file = Path(tempo_dir, "not_so_really_recent_file.txt")
            tempo_file.touch()
            sleep(3)
            self.assertTrue(
                is_file_older_than(Path(tempo_file), expiration_rotating_hours=0)
            )


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

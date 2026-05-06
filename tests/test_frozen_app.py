#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_frozen_app
    # for specific test
    python -m unittest tests.test_frozen_app.TestFrozenApp.test_is_frozen_app_false_by_default
"""

# standard
import unittest
from unittest.mock import patch

# project
from qgis_deployment_toolbelt.utils import frozen_app


# ############################################################################
# ########## Classes #############
# ################################


class TestFrozenApp(unittest.TestCase):
    """Test the helper to detect Python is bundled or not, with PyInstaller or not"""

    def test_is_frozen_app_false_by_default(self):
        """Test sys.frozen not set."""
        with patch.object(frozen_app.sys, "frozen", new=False, create=True):
            self.assertFalse(frozen_app.is_frozen_app())

    def test_is_frozen_app_true(self):
        """Test sys.frozen is set."""
        with patch.object(frozen_app.sys, "frozen", new=True, create=True):
            self.assertTrue(frozen_app.is_frozen_app())

    def test_is_running_pyinstaller_false_when_not_frozen(self):
        """frozen not set, but _MEIPASS exists."""
        with patch.object(frozen_app.sys, "frozen", new=False, create=True):
            with patch.object(
                frozen_app.sys, "_MEIPASS", new="/tmp/geotribu", create=True
            ):
                self.assertFalse(frozen_app.is_running_pyinstaller())

    def test_is_running_pyinstaller_false_when_no_meipass(self):
        """frozen set but no _MEIPASS."""
        with patch.object(frozen_app.sys, "frozen", new=True, create=True):
            if hasattr(frozen_app.sys, "_MEIPASS"):
                delattr(frozen_app.sys, "_MEIPASS")

            self.assertFalse(frozen_app.is_running_pyinstaller())

    def test_is_running_pyinstaller_true(self):
        """frozen and _MEIPASS both set."""
        with patch.object(frozen_app.sys, "frozen", new=True, create=True):
            with patch.object(frozen_app.sys, "_MEIPASS", new="/tmp/fake", create=True):
                self.assertTrue(frozen_app.is_running_pyinstaller())


if __name__ == "__main__":
    unittest.main()

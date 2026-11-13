#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_shortcuts_finder
"""

# standard lib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# project
from qgis_deployment_toolbelt.constants import QDT_SHORTCUT_DESCRIPTION_PREFIX
from qgis_deployment_toolbelt.shortcuts.finder import list_qdt_shortcuts


# ############################################################################
# ########## Classes #############
# ################################


class TestShortcutsFinder(unittest.TestCase):
    """Test shortcuts finder."""

    def test_list_qdt_shortcuts(self):
        """Only shortcuts with the QDT mark and an absolute profile folder are
        listed."""
        with tempfile.TemporaryDirectory(prefix="QDT_test_shortcuts_") as tmp_dir:
            shortcuts = {
                "qdt": (f"{QDT_SHORTCUT_DESCRIPTION_PREFIX} 0.50.0", Path(tmp_dir)),
                "user": ("Created by someone else", Path(tmp_dir)),
                "relative": (f"{QDT_SHORTCUT_DESCRIPTION_PREFIX} 0.50.0", Path("p")),
                "unreadable": None,
            }
            for name in shortcuts:
                Path(tmp_dir, f"{name}.lnk").touch()

            module = "qgis_deployment_toolbelt.shortcuts.finder"
            with (
                patch(f"{module}.get_user_desktop_folder", return_value=Path(tmp_dir)),
                patch(
                    f"{module}.get_user_startmenu_folder",
                    return_value=Path(tmp_dir, "not_existing"),
                ),
                patch(
                    f"{module}.read_shortcut",
                    side_effect=lambda shortcut_path: shortcuts[shortcut_path.stem],
                ),
            ):
                self.assertEqual(
                    list_qdt_shortcuts(".lnk"),
                    {Path(tmp_dir, "qdt.lnk"): Path(tmp_dir)},
                )


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

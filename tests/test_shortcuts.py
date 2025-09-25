#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_shortcuts
    # for specific test
    python -m unittest tests.test_shortcuts.TestShortcut.test_shortcut_creation
"""

# standard lib
import unittest
from pathlib import Path
from sys import platform as opersys

# project
from qgis_deployment_toolbelt.shortcuts.shortcuts_handler import ApplicationShortcut


# ############################################################################
# ########## Classes #############
# ################################


class TestShortcut(unittest.TestCase):
    """Test shortcut creation and deletion."""

    def test_shortcut_creation_complete(self):
        """Test creation of shortcut."""
        shortcut = ApplicationShortcut(
            name="QDT - Test shortcut complete",
            exec_path=Path(__file__),
            exec_arguments=("--test", "unit"),
            description="A test shortcut",
            icon_path=Path(__file__).parent / "icon.png",
            work_dir=Path(__file__).parent,
        )

        shortcuts_paths = shortcut.create(
            desktop=True,
            start_menu=True,
        )

        if opersys in ("linux", "win32"):
            self.assertIsInstance(shortcuts_paths, tuple)
            self.assertIsInstance(shortcuts_paths[0], Path)
            self.assertIsInstance(shortcuts_paths[1], Path)

            self.assertTrue(shortcuts_paths[0].exists())
            self.assertTrue(shortcuts_paths[1].exists())

            # clean up
            shortcuts_paths[0].unlink()
            shortcuts_paths[1].unlink()

    def test_shortcut_creation_minimal(self):
        """Test creation of shortcut."""
        shortcut = ApplicationShortcut(
            name="QDT - Test shortcut minimal",
            exec_path=Path(__file__),
            work_dir=Path(__file__).parent,
        )

        shortcuts_paths = shortcut.create(desktop=True, start_menu=True)

        if opersys in ("linux", "win32"):
            self.assertIsInstance(shortcuts_paths, tuple)
            self.assertIsInstance(shortcuts_paths[0], Path)
            self.assertIsInstance(shortcuts_paths[1], Path)

            self.assertTrue(shortcuts_paths[0].exists())
            self.assertTrue(shortcuts_paths[1].exists())

            # clean up
            shortcuts_paths[0].unlink()
            shortcuts_paths[1].unlink()

    def test_shortcut_bad_types(self):
        """Test shortcut TypeError raises."""
        with self.assertRaises(TypeError):
            ApplicationShortcut(
                name=["QDT - Test shortcut bad type"],
                exec_path=Path(__file__),
            )

        with self.assertRaises(TypeError):
            ApplicationShortcut(
                name="QDT - Test shortcut bad type",
                exec_path=[Path(__file__)],
            )

        with self.assertRaises(TypeError):
            ApplicationShortcut(
                name="QDT - Test shortcut bad type",
                exec_path=Path(__file__),
                exec_arguments="--test unit",
            )

        with self.assertRaises(TypeError):
            ApplicationShortcut(
                name="QDT - Test shortcut bad type",
                exec_path=Path(__file__),
                exec_arguments=("--test", "unit"),
                description=["A test shortcut"],
            )

        with self.assertRaises(TypeError):
            ApplicationShortcut(
                name="QDT - Test shortcut bad type",
                exec_path=Path(__file__),
                exec_arguments=("--test", "unit"),
                description="A test shortcut",
                icon_path=["icon.png"],
            )

        with self.assertRaises(TypeError):
            ApplicationShortcut(
                name="QDT - Test shortcut bad type",
                exec_path=Path(__file__),
                work_dir=["C:\\"],
            )


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

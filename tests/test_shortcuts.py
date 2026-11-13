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
import tempfile
import unittest
from os import environ
from pathlib import Path
from sys import platform as opersys
from unittest.mock import patch

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

    @unittest.skipUnless(opersys == "linux", "FreeDesktop shortcuts")
    def test_freedesktop_shortcut_quotes_profile_folder(self):
        """Executable path is quoted, profile folder is set as working directory and
        quoted in actions."""
        with (
            tempfile.TemporaryDirectory(prefix="QDT_test_shortcuts_") as tmp_dir,
            patch.dict(environ, {"HOME": tmp_dir}),
        ):
            profile_folder = Path(tmp_dir, "profiles", "unit test").resolve()
            profile_folder.mkdir(parents=True)
            desktop_path, _ = ApplicationShortcut(
                name="QDT - Unit test",
                exec_path=Path(__file__),
                work_dir=profile_folder,
            ).create(desktop=True, start_menu=False)

            lines = desktop_path.read_text(encoding="UTF-8").splitlines()
            self.assertIn(f'Exec="{Path(__file__)}"', lines)
            self.assertIn(f"Path={profile_folder}", lines)
            self.assertIn(f'Exec=xdg-open "{profile_folder}"', lines)
            self.assertTrue(
                any(
                    line.startswith("Exec=bash -c")
                    and line.endswith(f"gio trash '{profile_folder}'\"")
                    for line in lines
                )
            )


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

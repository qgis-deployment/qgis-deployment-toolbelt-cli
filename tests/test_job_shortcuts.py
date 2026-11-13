#! python3  # noqa E265

"""Usage from the repo root folder:

.. code-block:: python

    # for whole test
    python -m unittest tests.test_job_shortcuts
    # for specific
    python -m unittest tests.test_job_shortcuts.TestJobShortcuts.test_shortcut_not_created_for_not_installed_profile
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import tempfile
import unittest
from os import environ
from pathlib import Path
from unittest.mock import patch

# package
from qgis_deployment_toolbelt.jobs.job_shortcuts import JobShortcutsManager
from qgis_deployment_toolbelt.profiles.qdt_profile import QdtProfile
from qgis_deployment_toolbelt.shortcuts.manifest import (
    _read_qdt_managed_shortcuts_manifest,
)


# #############################################################################
# ########## Classes ###############
# ##################################


class TestJobShortcuts(unittest.TestCase):
    """Test shortcuts manager job."""

    def test_shortcut_not_created_for_not_installed_profile(self):
        """A shortcut must only target a profile installed by QDT (with its
        profile.json), otherwise QGIS launches an empty or partial profile."""
        job = JobShortcutsManager(
            options={
                "action": "create",
                "include": [{"label": "QGIS - Unit test", "profile": "unit_test"}],
            }
        )

        with tempfile.TemporaryDirectory(prefix="QDT_test_shortcuts_") as tmp_dir:
            installed_folder = Path(tmp_dir, "unit_test")
            cases = (
                # (state of the profile folder in QGIS, expected shortcuts created)
                ("absent", 0),
                # e.g. created by qplugins-synchronizer with profile_ref: downloaded
                ("plugins_only", 0),
                ("installed", 1),
            )
            for state, expected_shortcuts in cases:
                if state == "plugins_only":
                    installed_folder.joinpath("python/plugins").mkdir(parents=True)
                elif state == "installed":
                    installed_folder.joinpath("profile.json").write_text(
                        '{"name": "unit_test"}', encoding="UTF-8"
                    )

                with (
                    self.subTest(state=state),
                    patch.dict(
                        environ,
                        {
                            "QGIS_CUSTOM_CONFIG_PATH": tmp_dir,
                            "QDT_SHORTCUTS_MANIFEST_PATH": str(
                                Path(tmp_dir, "manifest.json")
                            ),
                        },
                    ),
                    patch(
                        "qgis_deployment_toolbelt.jobs.job_shortcuts.ApplicationShortcut"
                    ) as mock_shortcut,
                ):
                    qdt_profile = QdtProfile(
                        name="unit_test",
                        folder=Path(tmp_dir, "downloaded", "unit_test"),
                    )
                    self.assertEqual(qdt_profile.path_in_qgis, installed_folder)

                    with patch.object(
                        job, "list_downloaded_profiles", return_value=(qdt_profile,)
                    ):
                        job.run()

                    self.assertEqual(mock_shortcut.call_count, expected_shortcuts)

    def test_shortcut_not_created_for_profile_name_with_forbidden_chars(self):
        """A profile name with chars breaking the shortcut command line is refused."""
        with tempfile.TemporaryDirectory(prefix="QDT_test_shortcuts_") as tmp_dir:
            for profile_name, expected_shortcuts in (("QDT $HOME", 0), ("QDT Demo", 1)):
                Path(tmp_dir, profile_name, "profile.json").parent.mkdir()
                Path(tmp_dir, profile_name, "profile.json").write_text("{}")
                job = JobShortcutsManager(
                    options={
                        "action": "create",
                        "include": [{"label": "QGIS", "profile": profile_name}],
                    }
                )
                with (
                    self.subTest(profile_name=profile_name),
                    patch.dict(
                        environ,
                        {
                            "QGIS_CUSTOM_CONFIG_PATH": tmp_dir,
                            "QDT_SHORTCUTS_MANIFEST_PATH": str(
                                Path(tmp_dir, "manifest.json")
                            ),
                        },
                    ),
                    patch(
                        "qgis_deployment_toolbelt.jobs.job_shortcuts.ApplicationShortcut"
                    ) as mock_shortcut,
                ):
                    qdt_profile = QdtProfile(
                        name=profile_name,
                        folder=Path(tmp_dir, "downloaded", profile_name),
                    )
                    with patch.object(
                        job, "list_downloaded_profiles", return_value=(qdt_profile,)
                    ):
                        job.run()

                    self.assertEqual(mock_shortcut.call_count, expected_shortcuts)

    def test_created_shortcuts_are_recorded_in_manifest(self):
        """Created shortcuts are recorded in the manifest with their location and
        targeted profile folder."""
        job = JobShortcutsManager(
            options={
                "action": "create",
                "include": [
                    {
                        "label": "QGIS - Unit test",
                        "profile": "unit_test",
                        "desktop": True,
                    }
                ],
            }
        )

        with tempfile.TemporaryDirectory(prefix="QDT_test_shortcuts_") as tmp_dir:
            # in a folder which doesn't exist yet
            manifest_path = Path(tmp_dir, "qdt", "manifest.json")
            installed_folder = Path(tmp_dir, "unit_test")
            installed_folder.mkdir()
            installed_folder.joinpath("profile.json").write_text(
                '{"name": "unit_test"}', encoding="UTF-8"
            )
            desktop_shortcut = Path(tmp_dir, "Desktop", "QGIS - Unit test.lnk")
            startmenu_shortcut = Path(tmp_dir, "Programs", "QGIS - Unit test.lnk")

            with (
                patch.dict(
                    environ,
                    {
                        "QGIS_CUSTOM_CONFIG_PATH": tmp_dir,
                        "QDT_SHORTCUTS_MANIFEST_PATH": str(manifest_path),
                    },
                ),
                patch(
                    "qgis_deployment_toolbelt.jobs.job_shortcuts.ApplicationShortcut"
                ) as mock_shortcut,
            ):
                mock_shortcut.return_value.create.return_value = (
                    desktop_shortcut,
                    startmenu_shortcut,
                )
                qdt_profile = QdtProfile(
                    name="unit_test", folder=Path(tmp_dir, "downloaded", "unit_test")
                )
                with patch.object(
                    job, "list_downloaded_profiles", return_value=(qdt_profile,)
                ):
                    job.run()

            manifest = _read_qdt_managed_shortcuts_manifest(manifest_path)
            self.assertEqual(
                {
                    path: (entry["location"], entry["profile_folder"])
                    for path, entry in manifest.items()
                },
                {
                    str(desktop_shortcut): ("desktop", str(installed_folder)),
                    str(startmenu_shortcut): ("start_menu", str(installed_folder)),
                },
            )

    def test_read_corrupted_manifest(self):
        """A corrupted manifest is read as empty, with a warning."""
        with tempfile.TemporaryDirectory(prefix="QDT_test_shortcuts_") as tmp_dir:
            manifest_path = Path(tmp_dir, "manifest.json")
            manifest_path.write_text("not a JSON content", encoding="UTF-8")
            with self.assertLogs(
                "qgis_deployment_toolbelt.shortcuts.manifest", level="WARNING"
            ):
                self.assertEqual(
                    _read_qdt_managed_shortcuts_manifest(manifest_path), {}
                )


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

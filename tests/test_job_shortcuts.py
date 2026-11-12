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


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

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
        """A shortcut must only target a profile installed in QGIS, otherwise QGIS
        creates an empty one at launch."""
        job = JobShortcutsManager(
            options={
                "action": "create",
                "include": [{"label": "QGIS - Unit test", "profile": "unit_test"}],
            }
        )

        with tempfile.TemporaryDirectory(prefix="QDT_test_shortcuts_") as tmp_dir:
            for installed in (False, True):
                with (
                    self.subTest(installed=installed),
                    patch.dict(environ, {"QGIS_CUSTOM_CONFIG_PATH": tmp_dir}),
                    patch(
                        "qgis_deployment_toolbelt.jobs.job_shortcuts.ApplicationShortcut"
                    ) as mock_shortcut,
                ):
                    qdt_profile = QdtProfile(
                        name="unit_test",
                        folder=Path(tmp_dir, "downloaded", "unit_test"),
                    )
                    if installed:
                        qdt_profile.path_in_qgis.mkdir(parents=True)
                    self.assertEqual(
                        qdt_profile.path_in_qgis, Path(tmp_dir, "unit_test")
                    )

                    with patch.object(
                        job, "list_downloaded_profiles", return_value=(qdt_profile,)
                    ):
                        job.run()

                    self.assertEqual(mock_shortcut.call_count, int(installed))


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

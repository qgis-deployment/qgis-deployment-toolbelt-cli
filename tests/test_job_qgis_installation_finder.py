#! python3  # noqa E265

"""Usage from the repo root folder:

.. code-block:: python

    # for whole test
    python -m unittest tests.test_job_qgis_installation_finder
    # for specific
    python -m unittest tests.job_qgis_installation_finder.TestJobQgisInstallationFinder.test_get_latest_version_from_list
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import unittest
from os import environ
from unittest.mock import patch

# package
from qgis_deployment_toolbelt.constants import (
    ENV_VAR_QGIS_EXE_PATH,
    ENV_VAR_QGIS_VERSION,
)
from qgis_deployment_toolbelt.jobs.job_qgis_installation_finder import (
    JobQgisInstallationFinder,
)


# #############################################################################
# ########## Classes ###############
# ##################################


class TestJobQgisInstallationFinder(unittest.TestCase):
    """Test module."""

    # -- TESTS ---------------------------------------------------------
    def test_get_windows_startupinfo_kwargs_non_windows(self):
        """On non-Windows platforms, no startupinfo kwarg is built."""
        with patch(
            "qgis_deployment_toolbelt.jobs.job_qgis_installation_finder.opersys",
            "linux",
        ):
            self.assertEqual(
                JobQgisInstallationFinder._get_windows_hide_console_startupinfo(), {}
            )

    def test_get_windows_startupinfo_kwargs_windows(self):
        """On win32, a startupinfo requesting a hidden window is built.

        subprocess.STARTUPINFO and the STARTF_*/SW_* constants only exist on
        win32, so they are faked here to exercise the branch on any platform.
        """

        class _FakeStartupInfo:
            def __init__(self):
                self.dwFlags = 0
                self.wShowWindow = None

        with (
            patch(
                "qgis_deployment_toolbelt.jobs.job_qgis_installation_finder.opersys",
                "win32",
            ),
            patch("subprocess.STARTUPINFO", _FakeStartupInfo, create=True),
            patch("subprocess.STARTF_USESHOWWINDOW", 1, create=True),
            patch("subprocess.SW_HIDE", 0, create=True),
            patch("subprocess.CREATE_NO_WINDOW", 0x08000000, create=True),
        ):
            kwargs = JobQgisInstallationFinder._get_windows_hide_console_startupinfo()

        self.assertIn("startupinfo", kwargs)
        self.assertEqual(kwargs["startupinfo"].dwFlags, 1)
        self.assertEqual(kwargs["startupinfo"].wShowWindow, 0)

    def test_get_latest_version_from_list(self):
        """Test definition of latest version from a list of version"""
        self.assertEqual(
            JobQgisInstallationFinder._get_latest_version_from_list(
                ["3.25.1", "4.0.1", "4.1.0", "3.28.2"]
            ),
            "4.1.0",
        )

    def test_get_latest_matching_version_path(self):
        """Test definition of latest version from a list of version"""

        # Matching version
        self.assertEqual(
            JobQgisInstallationFinder._get_latest_matching_version_path(
                {
                    "3.25.1": "/path/to/3_25_1",
                    "3.25.8": "/path/to/3_25_8",
                    "3.25.2": "/path/to/3_25_2",
                },
                "3.25",
            ),
            "/path/to/3_25_8",
        )

        # No matching version
        self.assertIsNone(
            JobQgisInstallationFinder._get_latest_matching_version_path(
                {
                    "3.25.1": "/path/to/3_25_1",
                    "3.25.8": "/path/to/3_25_8",
                    "3.25.2": "/path/to/3_25_2",
                },
                "3.36",
            )
        )

    def test_get_latest_version_from_list_empty(self):
        """No versions given returns None."""
        self.assertIsNone(JobQgisInstallationFinder._get_latest_version_from_list([]))

    def test_get_latest_version_from_list_minor_multidigit(self):
        """Regression: a single-digit minor must not outrank a double-digit one.

        A plain lexicographic string sort ranks "3.8.0" above "3.44.0" because '8'
        sorts after '4' at the same character position, ignoring that "44" is a
        larger number than "8".
        """
        self.assertEqual(
            JobQgisInstallationFinder._get_latest_version_from_list(
                [
                    "2",
                    "3.8.0",
                    "4.2.1",
                    "3.44.0",
                ]
            ),
            "4.2.1",
        )

    def test_get_latest_version_from_list_patch_multidigit(self):
        """Regression: same bug at the patch level, e.g. late in an LTR branch's life."""
        self.assertEqual(
            JobQgisInstallationFinder._get_latest_version_from_list(
                ["3.34.9", "3.34.10"]
            ),
            "3.34.10",
        )

    def test_get_latest_version_from_list_does_not_mutate_input(self):
        """The input list is no longer sorted in place as a side effect."""
        versions = ["3.34.10", "3.34.9", "3.28.1"]
        original_order = list(versions)
        JobQgisInstallationFinder._get_latest_version_from_list(versions)
        self.assertEqual(versions, original_order)

    def test_get_latest_version_from_list_unparsable_is_ignored(self):
        """An unparsable version string is never selected, and doesn't raise."""
        self.assertEqual(
            JobQgisInstallationFinder._get_latest_version_from_list(
                ["3.40.11", "not-a-version"]
            ),
            "3.40.11",
        )

    def test_get_latest_matching_version_path_patch_multidigit(self):
        """Regression: version_priority selection was affected by the same bug."""
        self.assertEqual(
            JobQgisInstallationFinder._get_latest_matching_version_path(
                {
                    "3.34.1": "/path/to/3_34_1",
                    "3.34.9": "/path/to/3_34_9",
                    "3.34.10": "/path/to/3_34_10",
                },
                "3.34",
            ),
            "/path/to/3_34_10",
        )

    def test_get_installed_qgis_version_and_path_no_priority(self):
        """Without version_priority, the most recent found version is returned."""
        job = JobQgisInstallationFinder(options={})
        with (
            patch(
                "qgis_deployment_toolbelt.jobs.job_qgis_installation_finder.opersys",
                "linux",
            ),
            patch.object(
                JobQgisInstallationFinder,
                "_get_linux_installed_qgis_path",
                return_value={
                    "3.34.1": "/path/to/qgis-3.34",
                    "3.40.5": "/path/to/qgis-3.40",
                },
            ),
        ):
            result = job.get_installed_qgis_version_and_path()

        self.assertEqual(result, ("3.40.5", "/path/to/qgis-3.40"))

    def test_get_installed_qgis_version_and_path_with_priority(self):
        """The version and path returned match the version_priority option."""
        job = JobQgisInstallationFinder(options={"version_priority": ["3.34"]})
        with (
            patch(
                "qgis_deployment_toolbelt.jobs.job_qgis_installation_finder.opersys",
                "linux",
            ),
            patch.object(
                JobQgisInstallationFinder,
                "_get_linux_installed_qgis_path",
                return_value={
                    "3.34.1": "/path/to/qgis-3.34",
                    "3.40.5": "/path/to/qgis-3.40",
                },
            ),
        ):
            result = job.get_installed_qgis_version_and_path()

        self.assertEqual(result, ("3.34.1", "/path/to/qgis-3.34"))

    def test_get_installed_qgis_version_and_path_none_found(self):
        """No installation found returns None, not an empty tuple."""
        job = JobQgisInstallationFinder(options={})
        with (
            patch(
                "qgis_deployment_toolbelt.jobs.job_qgis_installation_finder.opersys",
                "linux",
            ),
            patch.object(
                JobQgisInstallationFinder,
                "_get_linux_installed_qgis_path",
                return_value={},
            ),
        ):
            self.assertIsNone(job.get_installed_qgis_version_and_path())

    def test_get_installed_qgis_path_backward_compatible(self):
        """The deprecated path-only method still returns the path alone."""
        job = JobQgisInstallationFinder(options={})
        with (
            patch(
                "qgis_deployment_toolbelt.jobs.job_qgis_installation_finder.opersys",
                "linux",
            ),
            patch.object(
                JobQgisInstallationFinder,
                "_get_linux_installed_qgis_path",
                return_value={"3.40.5": "/path/to/qgis-3.40"},
            ),
        ):
            self.assertEqual(job.get_installed_qgis_path(), "/path/to/qgis-3.40")

    def test_run_exports_version_after_search(self):
        """QDT_QGIS_VERSION is exported alongside QDT_QGIS_EXE_PATH after a search."""
        job = JobQgisInstallationFinder(options={})
        environ.pop(ENV_VAR_QGIS_EXE_PATH, None)
        environ.pop(ENV_VAR_QGIS_VERSION, None)
        self.addCleanup(environ.pop, ENV_VAR_QGIS_EXE_PATH, None)
        self.addCleanup(environ.pop, ENV_VAR_QGIS_VERSION, None)

        with (
            patch(
                "qgis_deployment_toolbelt.jobs.job_qgis_installation_finder.opersys",
                "linux",
            ),
            patch.object(job, "run_needed", return_value=True),
            patch.object(
                job,
                "get_installed_qgis_version_and_path",
                return_value=("3.40.5", "/path/to/qgis-3.40"),
            ),
        ):
            job.run()

        self.assertEqual(environ.get(ENV_VAR_QGIS_EXE_PATH), "/path/to/qgis-3.40")
        self.assertEqual(environ.get(ENV_VAR_QGIS_VERSION), "3.40.5")

    def test_run_exports_version_when_exe_path_already_defined(self):
        """QDT_QGIS_VERSION is still exported when the job itself is skipped."""
        job = JobQgisInstallationFinder(options={})
        environ.pop(ENV_VAR_QGIS_VERSION, None)
        self.addCleanup(environ.pop, ENV_VAR_QGIS_VERSION, None)

        with patch.object(job, "run_needed", return_value=False):
            job.CACHE_DETECTED_QGIS_VERSION = "3.28.15"
            job.run()

        self.assertEqual(environ.get(ENV_VAR_QGIS_VERSION), "3.28.15")

    def test_run_does_not_export_version_when_undetectable(self):
        """No version is exported when the skip branch could not detect one."""
        job = JobQgisInstallationFinder(options={})
        environ.pop(ENV_VAR_QGIS_VERSION, None)
        self.addCleanup(environ.pop, ENV_VAR_QGIS_VERSION, None)

        with patch.object(job, "run_needed", return_value=False):
            job.CACHE_DETECTED_QGIS_VERSION = None
            job.run()

        self.assertNotIn(ENV_VAR_QGIS_VERSION, environ)

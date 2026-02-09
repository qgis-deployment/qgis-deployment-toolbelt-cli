#! python3  # noqa E265

"""Usage from the repo root folder:

.. code-block:: python

    # for whole test
    python -m unittest tests.test_job_default_profile_setter
    # for specific
    python -m unittest tests.test_job_default_profile_setter.TestJobDefaultProfileSetter.test_job_default_profile_setter_run
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import tempfile
import unittest
from os import environ, getenv
from pathlib import Path
from sys import platform as opersys

# package
from qgis_deployment_toolbelt.jobs.job_default_profile_setter import (
    JobDefaultProfileSetter,
)


if opersys == "win32":
    from qgis_deployment_toolbelt.utils.win32utils import (
        qgis_command_user_hkey,
        read_registry_value,
    )


# #############################################################################
# ########## Classes ###############
# ##################################
class TestJobDefaultProfileSetter(unittest.TestCase):
    """Test default profile setter job."""

    # -- Standard methods --------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """Executed when module is loaded before any test."""
        cls.default_profile_setter_job = JobDefaultProfileSetter(
            options={"profile": "qdt_test_profile_minimal"}
        )
        cls.default_profile_setter_job.qgis_profiles_path = (
            Path(tempfile.mkdtemp()) / "profiles"
        )
        cls.default_profile_setter_job.qgis_profiles_path.mkdir(
            parents=True, exist_ok=True
        )
        cls.profiles_ini = (
            cls.default_profile_setter_job.qgis_profiles_path / "profiles.ini"
        )

        # simulate a QGIS profiles folder structure in the temp folder
        fixtures_profiles_folder = Path("tests/fixtures/profiles")
        for p in fixtures_profiles_folder.glob("good_profile_*.json"):
            dest_file = cls.default_profile_setter_job.qgis_profiles_path.joinpath(
                f"test_{p.stem}/profile.json"
            )
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            dest_file.write_text(p.read_text(encoding="UTF-8"), encoding="UTF-8")

    def tearDown(self):
        """Executed after each test."""
        self.profiles_ini.unlink(missing_ok=True)

    # -- TESTS --------------------------------------------------------------------
    def test_job_default_profile_setter_run(self):
        """Run the job."""
        self.assertFalse(self.profiles_ini.exists())
        self.default_profile_setter_job.run()
        self.assertTrue(self.profiles_ini.exists())

        content = self.profiles_ini.read_text()
        expected_content = "[core]\ndefaultProfile=qdt_test_profile_minimal"
        self.assertEqual(content, expected_content)

    def test_job_default_profile_setter_run_with_existing_profiles_ini(self):
        """Run the job with existing profiles.ini."""
        # first without selectionPolicy
        self.profiles_ini.write_text("[core]\ndefaultProfile=existing_profile")
        self.default_profile_setter_job.run()
        self.assertTrue(self.profiles_ini.exists())

        content = self.profiles_ini.read_text()
        expected_content = "[core]\ndefaultProfile=qdt_test_profile_minimal\n\n"
        self.assertEqual(content, expected_content)

        # then with selectionPolicy
        self.profiles_ini.write_text(
            "[core]\ndefaultProfile=existing_profile\nselectionPolicy=2"
        )
        self.default_profile_setter_job.run()
        self.assertTrue(self.profiles_ini.exists())

        content = self.profiles_ini.read_text()
        expected_content = (
            "[core]\ndefaultProfile=qdt_test_profile_minimal\nselectionPolicy=2\n\n"
        )
        self.assertEqual(content, expected_content)

    def test_job_default_profile_setter_run_with_force_profile_selection_policy(self):
        """Run the job with force profile selection policy."""
        self.default_profile_setter_job.options["force_profile_selection_policy"] = 1

        # first without profiles.ini
        self.default_profile_setter_job.run()
        self.assertTrue(self.profiles_ini.exists())
        content = self.profiles_ini.read_text()
        expected_content = (
            "[core]\ndefaultProfile=qdt_test_profile_minimal\nselectionPolicy=1"
        )
        self.assertEqual(content, expected_content)

        # then with existing profiles.ini
        self.profiles_ini.write_text("[core]\ndefaultProfile=existing_profile")
        self.default_profile_setter_job.run()
        self.assertTrue(self.profiles_ini.exists())

        content = self.profiles_ini.read_text()
        expected_content = (
            "[core]\ndefaultProfile=qdt_test_profile_minimal\nselectionPolicy=1\n\n"
        )
        self.assertEqual(content, expected_content)

        # then with existing profiles.ini and existing selectionPolicy
        self.profiles_ini.write_text(
            "[core]\ndefaultProfile=existing_profile\nselectionPolicy=2"
        )
        self.default_profile_setter_job.run()
        self.assertTrue(self.profiles_ini.exists())

        content = self.profiles_ini.read_text()
        expected_content = (
            "[core]\ndefaultProfile=qdt_test_profile_minimal\nselectionPolicy=1\n\n"
        )
        self.assertEqual(content, expected_content)

    @unittest.skipUnless(
        opersys == "win32" and getenv("GITHUB_ACTIONS", False),
        "Test specific to Windows and run only in CI to avoid modifying registry.",
    )
    def test_job_default_profile_setter_run_with_force_profile_file_association(self):
        """Run the job with force profile file association."""
        self.default_profile_setter_job.options["force_profile_file_association"] = True
        self.default_profile_setter_job.options["force_registry_key_creation"] = True
        environ["QDT_QGIS_EXE_PATH"] = "/usr/bin/toto"

        self.default_profile_setter_job.run()
        self.assertTrue(self.profiles_ini.exists())

        reg_value = read_registry_value(
            qgis_command_user_hkey,
            "",
        )
        expected_reg_value = (
            '"\\usr\\bin\\toto" --profile "qdt_test_profile_minimal" "%1"'
        )
        self.assertEqual(reg_value, expected_reg_value)

    @unittest.skipUnless(
        opersys == "win32" and getenv("GITHUB_ACTIONS", False),
        "Test specific to Windows and run only in CI to avoid modifying registry.",
    )
    def test_job_default_profile_setter_run_with_profile_file_association_arguments(
        self,
    ):
        """Run the job with force profile file association."""
        self.default_profile_setter_job.options["force_profile_file_association"] = True
        self.default_profile_setter_job.options["force_registry_key_creation"] = True
        self.default_profile_setter_job.options[
            "profile_file_association_arguments"
        ] = "--noversioncheck"
        environ["QDT_QGIS_EXE_PATH"] = "/usr/bin/toto"

        self.default_profile_setter_job.run()
        self.assertTrue(self.profiles_ini.exists())

        reg_value = read_registry_value(
            qgis_command_user_hkey,
            "",
        )
        expected_reg_value = '"\\usr\\bin\\toto" --profile "qdt_test_profile_minimal" --noversioncheck "%1"'
        self.assertEqual(reg_value, expected_reg_value)

        self.default_profile_setter_job.options["force_profile_selection_policy"] = 2

        self.default_profile_setter_job.run()
        self.assertTrue(self.profiles_ini.exists())
        content = self.profiles_ini.read_text()
        expected_content = (
            "[core]\ndefaultProfile=qdt_test_profile_minimal\nselectionPolicy=2\n\n"
        )
        self.assertEqual(content, expected_content)

        self.default_profile_setter_job.options["force_profile_selection_policy"] = 0

        self.default_profile_setter_job.run()
        self.assertTrue(self.profiles_ini.exists())
        content = self.profiles_ini.read_text()
        expected_content = (
            "[core]\ndefaultProfile=qdt_test_profile_minimal\nselectionPolicy=0\n\n"
        )
        self.assertEqual(content, expected_content)

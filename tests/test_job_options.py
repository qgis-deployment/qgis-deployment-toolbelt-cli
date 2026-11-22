#! python3  # noqa E265

"""Usage from the repo root folder:

.. code-block:: python

    # for whole test
    python -m unittest tests.test_job_options
    # for specific
    python -m unittest tests.test_job_options.TestJobOptions.test_defaults_applied
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import unittest
from typing import Literal

# 3rd party
from pydantic import ValidationError

# package
from qgis_deployment_toolbelt.exceptions import (
    JobOptionBadNameError,
    JobOptionBadValueError,
    JobOptionBadValueTypeError,
    JobOptionMissingError,
)
from qgis_deployment_toolbelt.jobs.job_profiles_synchronizer import (
    JobProfilesSynchronizer,
)
from qgis_deployment_toolbelt.jobs.options import JobOptions


# #############################################################################
# ########## Classes ###############
# ##################################


class ItemOptionsFixture(JobOptions):
    """Options of a nested item."""

    label: str


class OptionsFixture(JobOptions):
    """Options covering the default values and errors cases."""

    mode: Literal["fast", "safe"] = "safe"
    threads: int = 5
    strict: bool = False
    scopes: list[str] = ["plugins_cache"]
    policy: Literal["trash", "delete"] | None = None
    items: list[ItemOptionsFixture] = []
    source: str


class TestJobOptions(unittest.TestCase):
    """Test the base model of jobs options."""

    def test_defaults_applied(self):
        """Options not set get their default value, set ones are kept."""
        options = OptionsFixture.from_dict(
            {"source": "here", "threads": 2}, job_id="test"
        )

        self.assertEqual(options.source, "here")
        self.assertEqual(options.threads, 2)
        self.assertEqual(options.mode, "safe")
        self.assertIs(options.strict, False)
        self.assertEqual(options.scopes, ["plugins_cache"])
        self.assertIsNone(options.policy)

    def test_mutable_default_not_shared(self):
        """Each instance gets its own copy of a mutable default value."""
        first = OptionsFixture.from_dict({"source": "here"}, job_id="test")
        second = OptionsFixture.from_dict({"source": "here"}, job_id="test")

        first.scopes.append("plugins_installed")

        self.assertEqual(second.scopes, ["plugins_cache"])

    def test_nested_options(self):
        """Nested options are validated as models."""
        options = OptionsFixture.from_dict(
            {"source": "here", "items": [{"label": "QGIS"}]}, job_id="test"
        )

        self.assertEqual(options.items[0].label, "QGIS")

    def test_read_only(self):
        """Validated options can't be modified."""
        options = OptionsFixture.from_dict({"source": "here"}, job_id="test")

        with self.assertRaises(ValidationError):
            options.mode = "fast"

    def test_invalid_options(self):
        """Invalid options raise the matching QDT errors, naming the job and the
        option."""
        cases = (
            ({"source": "here", "unknown": 1}, JobOptionBadNameError, "unknown"),
            ({}, JobOptionMissingError, "source"),
            ({"source": 1}, JobOptionBadValueTypeError, "source"),
            # strict mode: no conversion from string
            ({"source": "here", "threads": "5"}, JobOptionBadValueTypeError, "threads"),
            ({"source": "here", "strict": "yes"}, JobOptionBadValueTypeError, "strict"),
            ({"source": "here", "mode": "slow"}, JobOptionBadValueError, "mode"),
            ({"source": "here", "policy": "keep"}, JobOptionBadValueError, "policy"),
            ({"source": "here", "items": [{}]}, JobOptionMissingError, "items.0.label"),
        )
        for raw_options, expected_error, option_name in cases:
            with (
                self.subTest(options=raw_options),
                self.assertRaises(expected_error) as ctx,
            ):
                OptionsFixture.from_dict(raw_options, job_id="test-job")
            self.assertIn("test-job", str(ctx.exception))
            self.assertIn(f"'{option_name}'", str(ctx.exception))

    def test_bad_value_lists_accepted_values(self):
        """The error on a closed set of values lists the accepted ones."""
        with self.assertRaises(JobOptionBadValueError) as ctx:
            OptionsFixture.from_dict({"source": "here", "mode": "slow"}, job_id="test")

        self.assertIn("fast,safe", str(ctx.exception))

    def test_options_not_a_mapping(self):
        """Options must be a mapping."""
        for raw_options in (None, ["source"], "source"):
            with self.subTest(options=raw_options), self.assertRaises(TypeError):
                OptionsFixture.from_dict(raw_options, job_id="test")


class TestJobProfilesSynchronizerOptions(unittest.TestCase):
    """Test the options of the first job migrated to JobOptions."""

    def test_sync_mode_default(self):
        """Without sync_mode, the documented default is used."""
        job = JobProfilesSynchronizer(options={})

        self.assertEqual(job.options.sync_mode, "only_missing")

    def test_sync_mode_set(self):
        """A valid sync_mode is kept, an invalid one is rejected."""
        job = JobProfilesSynchronizer(options={"sync_mode": "overwrite"})
        self.assertEqual(job.options.sync_mode, "overwrite")

        with self.assertRaises(JobOptionBadValueError):
            JobProfilesSynchronizer(options={"sync_mode": "always"})


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()

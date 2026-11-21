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
from qgis_deployment_toolbelt.jobs.options import Choice, JobOption, JobOptions, Type


# #############################################################################
# ########## Classes ###############
# ##################################


class OptionsFixture(JobOptions):
    """Options covering the option kinds and the default values cases."""

    mode = Choice(("fast", "safe"), default="safe")
    threads = Type(int, default=5)
    scopes = Type(list, default=["plugins_cache"])
    policy = Choice(("trash", "delete"), default=None)
    source = Type(str)


class ChildOptionsFixture(OptionsFixture):
    """Options inheriting from OptionsFixture."""

    strict = Type(bool, default=False)


class TestJobOptions(unittest.TestCase):
    """Test declarative job options."""

    def test_defaults_applied(self):
        """Options not set get their default value, set ones are kept."""
        options = OptionsFixture.from_dict(
            {"source": "here", "threads": 2}, job_id="test"
        )

        self.assertEqual(options.source, "here")
        self.assertEqual(options.threads, 2)
        self.assertEqual(options.mode, "safe")
        self.assertEqual(options.scopes, ["plugins_cache"])
        self.assertIsNone(options.policy)

    def test_falsy_default_applied(self):
        """A falsy default value (False, 0...) is applied like any other one."""
        options = ChildOptionsFixture.from_dict({"source": "here"}, job_id="test")

        self.assertIs(options.strict, False)

    def test_mutable_default_not_shared(self):
        """Each instance gets its own copy of a mutable default value."""
        first = OptionsFixture.from_dict({"source": "here"}, job_id="test")
        second = OptionsFixture.from_dict({"source": "here"}, job_id="test")

        first.scopes.append("plugins_installed")

        self.assertEqual(second.scopes, ["plugins_cache"])
        self.assertEqual(OptionsFixture.scopes.default, ["plugins_cache"])

    def test_inherited_options(self):
        """Options declared on parent classes are inherited."""
        self.assertEqual(
            list(ChildOptionsFixture.declared_options()),
            ["mode", "threads", "scopes", "policy", "source", "strict"],
        )

    def test_class_access_returns_option(self):
        """On the class, the attribute is the option itself, not a value."""
        self.assertIsInstance(OptionsFixture.mode, JobOption)
        self.assertEqual(OptionsFixture.mode.name, "mode")
        self.assertTrue(OptionsFixture.source.required)
        self.assertFalse(OptionsFixture.policy.required)

    def test_read_only(self):
        """Validated options can't be modified."""
        options = OptionsFixture.from_dict({"source": "here"}, job_id="test")

        with self.assertRaises(AttributeError):
            options.mode = "fast"

    def test_as_dict_and_repr(self):
        """Options values can be exported as a dict and are listed in repr."""
        options = OptionsFixture.from_dict({"source": "here"}, job_id="test")

        self.assertEqual(
            options.as_dict(),
            {
                "mode": "safe",
                "threads": 5,
                "scopes": ["plugins_cache"],
                "policy": None,
                "source": "here",
            },
        )
        self.assertIn("mode='safe'", repr(options))

    def test_invalid_options(self):
        """Invalid options raise the matching QDT errors."""
        cases = (
            ({"source": "here", "unknown": 1}, JobOptionBadNameError),
            ({}, JobOptionMissingError),
            ({"source": 1}, JobOptionBadValueTypeError),
            ({"source": "here", "mode": "slow"}, JobOptionBadValueError),
            ({"source": "here", "policy": None}, JobOptionBadValueError),
        )
        for raw_options, expected_error in cases:
            with (
                self.subTest(options=raw_options),
                self.assertRaises(expected_error) as ctx,
            ):
                OptionsFixture.from_dict(raw_options, job_id="test-job")
            self.assertIn("test-job", str(ctx.exception))

    def test_options_not_a_mapping(self):
        """Options must be a mapping."""
        for raw_options in (None, ["source"], "source"):
            with self.subTest(options=raw_options), self.assertRaises(TypeError):
                OptionsFixture.from_dict(raw_options, job_id="test")

    def test_invalid_default_fails_at_declaration(self):
        """A default value which breaks the option rules fails when the class is
        declared. Python < 3.12 wraps errors raised in __set_name__ in RuntimeError.
        """
        with self.assertRaises((JobOptionBadValueError, RuntimeError)):

            class BadChoiceDefault(JobOptions):
                mode = Choice(("fast", "safe"), default="slow")

        with self.assertRaises((JobOptionBadValueTypeError, RuntimeError)):

            class BadTypeDefault(JobOptions):
                threads = Type(int, default="5")

    def test_get_default_of_required_option(self):
        """A required option has no default value to get."""
        with self.assertRaises(ValueError):
            OptionsFixture.source.get_default()


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

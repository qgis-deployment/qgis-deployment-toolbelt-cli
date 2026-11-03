#! python3  # noqa E265

"""Usage from the repo root folder:

.. code-block:: python

    # for whole test
    python -m unittest tests.test_exceptions
    # for specific
    python -m unittest tests.test_exceptions.TestExceptions.test_qdt_error_base
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import unittest
from pathlib import Path

# project
from qgis_deployment_toolbelt.exceptions import (
    InvalidScenarioError,
    JobOptionBadNameError,
    JobOptionBadValueError,
    JobOptionBadValueTypeError,
    QdtError,
    QgisCustomizationXmlError,
    QgisInstallNotFoundError,
)


# #############################################################################
# ########## Classes ###############
# ##################################


class TestExceptions(unittest.TestCase):
    """Test custom exceptions."""

    def test_qdt_error_base(self):
        """Test that custom exceptions are QdtError and keep their built-in base,
        so that existing except clauses still match."""
        cases = (
            (JobOptionBadNameError("job", "bad", ("a", "b")), KeyError),
            (JobOptionBadValueError("job", "opt", "val", "cond"), ValueError),
            (JobOptionBadValueTypeError("job", "opt", 1, ("str",)), TypeError),
            (QgisCustomizationXmlError(Path("x.xml"), "reason"), ValueError),
            (InvalidScenarioError(Path("s.qdt.yml"), "reason"), ValueError),
            (QgisInstallNotFoundError(), Exception),
        )
        for error, builtin_base in cases:
            with self.subTest(error=type(error).__name__):
                self.assertIsInstance(error, QdtError)
                self.assertIsInstance(error, builtin_base)

    def test_qdt_error_str(self):
        """Test that str() returns the message, without the quotes added by
        KeyError.__str__."""
        error = JobOptionBadNameError("job", "bad", ("a", "b"))
        self.assertEqual(str(error), error.message)
        self.assertFalse(str(error).startswith("'"))

        # no message attribute: default representation
        self.assertEqual(str(QdtError("plain")), "plain")
        self.assertEqual(str(QdtError()), "")

    def test_invalid_scenario_error_message(self):
        """Test that the message holds the scenario location, as a resolved path
        for a file or as given for a buffer name."""
        scenario_path = Path("scenario.qdt.yml")
        error = InvalidScenarioError(scenario_path=scenario_path, reason="bad YAML")
        self.assertIn(str(scenario_path.resolve()), str(error))
        self.assertIn("bad YAML", str(error))

        error = InvalidScenarioError(scenario_path="BytesIO", reason="bad YAML")
        self.assertIn("'BytesIO'", str(error))


# #############################################################################
# ######## Standalone ##############
# ##################################
if __name__ == "__main__":
    unittest.main()

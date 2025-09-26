#! python3  # noqa E265

"""Usage from the repo root folder:

.. code-block:: python

    # for whole test
    python -m unittest tests.test_jobs_launch
    # for specific
    python -m unittest tests.test_jobs_launch.TestJobsLaunch.test_jobs_launcher
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import unittest
from pathlib import Path

# package
from qgis_deployment_toolbelt.jobs import JobsOrchestrator
from qgis_deployment_toolbelt.scenarios.scenario_reader import ScenarioReader


# #############################################################################
# ########## Classes ###############
# ##################################


class TestJobsLaunch(unittest.TestCase):
    """Test module."""

    # -- Standard methods --------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """Executed when module is loaded before any test."""
        cls.good_scenario_files = sorted(
            Path("tests/fixtures/").glob("scenarios/good_*.y*ml")
        )

    # -- TESTS ---------------------------------------------------------
    def test_jobs_launcher(self):
        """Test YAML loader"""
        steps_ok = []
        orchestrator = JobsOrchestrator()

        for i in self.good_scenario_files:
            scenario = ScenarioReader(in_yaml=i)
            for step in scenario.steps:
                if step.get("uses") not in orchestrator.jobs_ids:
                    continue
                else:
                    steps_ok.append(step)

        for step in steps_ok:
            job = orchestrator.init_job_class_from_id(
                job_id=step.get("uses"), options=step.get("with")
            )
            self.assertIsNotNone(job)

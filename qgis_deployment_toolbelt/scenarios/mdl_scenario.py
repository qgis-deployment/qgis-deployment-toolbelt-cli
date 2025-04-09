#! python3  # noqa: E265

"""
    QDT Scenario's metadata section.

    Author: Julien Moura (https://github.com/guts)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from dataclasses import dataclass

# project
from qgis_deployment_toolbelt.scenarios.mdl_scenario_metadata import ScenarioMetadata

# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################


@dataclass
class QdtScenario:
    """Model describing a QDT scenario."""

    metadata: ScenarioMetadata
    settings: dict
    steps: list[dict]

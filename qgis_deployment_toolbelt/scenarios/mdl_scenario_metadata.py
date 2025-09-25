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

# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################


@dataclass
class ScenarioMetadata:
    """Model describing the metadata section of a QDT scenario."""

    # required
    id: str
    title: str
    # optional
    description: str | None = None

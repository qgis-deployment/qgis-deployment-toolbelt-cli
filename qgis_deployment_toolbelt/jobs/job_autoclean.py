#! python3  # noqa: E265

"""
    QDT autocleaner.

    Author: Julien Moura (https://github.com/guts)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from pathlib import Path

# package
from qgis_deployment_toolbelt.jobs.generic_job import GenericJob
from qgis_deployment_toolbelt.utils.file_stats import is_file_older_than
from qgis_deployment_toolbelt.utils.trash_or_delete import move_files_to_trash_or_delete

# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################


class JobAutoclean(GenericJob):
    """
    Job to clean expired QDT resources (logs, plugins archives...) which are older than
    a specified frequency.
    """

    ID: str = "qdt-autoclean"
    OPTIONS_SCHEMA: dict = {
        "delay": {
            "type": int,
            "required": False,
            "default": 730,
            "possible_values": range(1, 1000),
            "condition": None,
        },
    }

    def __init__(self, options: dict) -> None:
        """Instantiate the class.

        :param dict options:  job options.
        """
        super().__init__()
        self.options: dict = self.validate_options(options)

    def run(self) -> None:
        """Execute job logic."""
        li_files_to_be_deleted: list[Path] = []

        # clean logs
        for log_file in self.qdt_logs_folder.glob("*.log"):
            if is_file_older_than(
                local_file_path=log_file,
                expiration_rotating_hours=self.options.get("delay", 730),
            ):
                logger.debug(f"Autoclean - LOGS - Outdated file: {log_file}")
                li_files_to_be_deleted.append(log_file)

        # clean plugins archives
        for plugin_archive in self.qdt_plugins_folder.glob("*.zip"):
            if is_file_older_than(
                local_file_path=plugin_archive,
                expiration_rotating_hours=self.options.get("delay", 730),
            ):
                logger.debug(
                    f"Autoclean - PLUGIN ARCHIVE - Outdated file: {plugin_archive}"
                )
                li_files_to_be_deleted.append(plugin_archive)

        move_files_to_trash_or_delete(files_to_trash=li_files_to_be_deleted)

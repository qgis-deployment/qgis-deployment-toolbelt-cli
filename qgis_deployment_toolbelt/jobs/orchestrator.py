#! python3  # noqa: E265

"""
Read and validate scenario files.

Author: Julien Moura (https://github.com/guts, Oslandia)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from os import environ

# project
from qgis_deployment_toolbelt.jobs.generic_job import GenericJob
from qgis_deployment_toolbelt.jobs.job_default_profile_setter import (
    JobDefaultProfileSetter,
)
from qgis_deployment_toolbelt.jobs.job_environment_variables import (
    JobEnvironmentVariables,
)
from qgis_deployment_toolbelt.jobs.job_plugins_downloader import JobPluginsDownloader
from qgis_deployment_toolbelt.jobs.job_plugins_synchronizer import (
    JobPluginsSynchronizer,
)
from qgis_deployment_toolbelt.jobs.job_profiles_downloader import JobProfilesDownloader
from qgis_deployment_toolbelt.jobs.job_profiles_synchronizer import (
    JobProfilesSynchronizer,
)
from qgis_deployment_toolbelt.jobs.job_qgis_installation_finder import (
    JobQgisInstallationFinder,
)
from qgis_deployment_toolbelt.jobs.job_shortcuts import JobShortcutsManager
from qgis_deployment_toolbelt.jobs.job_splash_screen import JobSplashScreenManager


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)

# #############################################################################
# ########## Classes ###############
# ##################################


class JobsOrchestrator:
    """Orchestrate jobs."""

    JOBS: tuple = (
        JobDefaultProfileSetter,
        JobEnvironmentVariables,
        JobPluginsDownloader,
        JobPluginsSynchronizer,
        JobProfilesDownloader,
        JobProfilesSynchronizer,
        JobShortcutsManager,
        JobSplashScreenManager,
        JobQgisInstallationFinder,
    )
    PACKAGE_NAME: str = "qgis_deployment_toolbelt.jobs"

    def __init__(self) -> None:
        """Instanciate orchestrator."""
        # log environment variables prefixed with QDT_
        qdt_env_vars = {
            env_var: value
            for env_var, value in environ.items()
            if env_var.startswith("QDT_")
        }
        if nb_qdt_envvars := len(qdt_env_vars):
            logger.debug(f"{nb_qdt_envvars} environment variables related to QDT:")
            for var_name, var_value in qdt_env_vars.items():
                logger.debug(f"{var_name}={var_value}")

    @property
    def jobs_ids(self) -> tuple[str, ...]:
        """Returns available jobs ID.

        Returns:
            tuple[str]: tuple of jobs ids
        """
        return tuple([job.ID for job in self.JOBS])

    def get_job_module_from_id(self, job_id: str) -> GenericJob | None:
        """Get job class from id.

        :param str job_id: job identifier (as defined in scenario file)
        :return object: Job class
        """
        for job in self.JOBS:
            if job.ID == job_id:
                return job

    def init_job_class_from_id(self, job_id: str, options: dict) -> GenericJob | None:
        """Get job class from id and instanciate it with options.

        :param str job_id: job identifier (i.e. "qprofiles-manager")
        :param dict options: job options

        :return object: instanciated job class with options
        """
        if job := self.get_job_module_from_id(job_id):
            return job(options)

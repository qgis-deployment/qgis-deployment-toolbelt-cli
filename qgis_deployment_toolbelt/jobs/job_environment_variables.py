#! python3  # noqa: E265

"""
Tools to manage the environment setup (variables, etc.)

Author: Julien Moura (https://github.com/guts)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
import os
from os.path import expanduser, expandvars
from pathlib import Path
from sys import platform as opersys

# package
from qgis_deployment_toolbelt.jobs.generic_job import GenericJob
from qgis_deployment_toolbelt.utils.check_path import (
    check_path_exists,
    check_var_can_be_path,
)
from qgis_deployment_toolbelt.utils.url_helpers import check_str_is_url


# conditional import
if opersys == "linux":
    from qgis_deployment_toolbelt.utils.linux_utils import (
        delete_environment_variable,
        refresh_environment,
        set_environment_variable,
    )
elif opersys == "win32":
    from qgis_deployment_toolbelt.utils.win32utils import (
        delete_environment_variable,
        refresh_environment,
        set_environment_variable,
    )

# #############################################################################
# ########## Globals ###############
# ##################################


# logs
logger = logging.getLogger(__name__)

# #############################################################################
# ########## Classes ###############
# ##################################


class JobEnvironmentVariables(GenericJob):
    """
    Class to manage the environment variables of QGIS installation.
    """

    ID: str = "manage-env-vars"
    OPTIONS_SCHEMA: dict = {
        "action": {
            "type": str,
            "required": False,
            "default": "add",
            "possible_values": ("add", "remove"),
            "condition": "in",
        },
        "name": {
            "type": str,
            "required": True,
            "default": None,
            "possible_values": None,
            "condition": None,
        },
        "scope": {
            "type": str,
            "required": False,
            "default": "user",
            "possible_values": ("system", "user"),
            "condition": "in",
        },
        "value": {
            "type": (bool, int, str, list),
            "required": False,
            "default": None,
            "possible_values": None,
            "condition": None,
        },
        "value_type": {
            "type": str,
            "required": False,
            "default": "str",
            "possible_values": ("bool", "path", "str", "url"),
            "condition": "in",
        },
    }

    def __init__(self, options: list[dict]) -> None:
        """Instantiate the class.
        Args:
            options (List[dict]): list of dictionary with environment variables to set
            or remove.
        """

        super().__init__()
        self.options: list[dict] = [self.validate_options(opt) for opt in options]

    def run(self) -> None:
        """Apply environment variables from dictionary to the system."""

        if opersys not in ("linux", "win32"):
            logger.error(f"This job does not support your operating system: {opersys}")
            return

        for env_var in self.options:
            if env_var.get("action") == "add":
                try:
                    envvar_name = env_var.get("name", None)
                    envvar_value = self.prepare_value(
                        value=env_var.get("value", None),
                        value_type=env_var.get("value_type", None),
                    )
                    set_environment_variable(
                        envvar_name=envvar_name,
                        envvar_value=envvar_value,
                        scope=env_var.get("scope", None),
                    )
                    # Add to local environnement to be used in other QDT jobs
                    os.environ[envvar_name] = envvar_value
                except NameError:
                    logger.debug(
                        f"Variable name '{env_var.get('name')}' is not defined"
                    )
            elif env_var.get("action") == "remove":
                try:
                    envvar_name = env_var.get("name", None)
                    delete_environment_variable(
                        envvar_name=envvar_name,
                        scope=env_var.get("scope", None),
                    )
                    # Remove from local environnement so it won't be used in other QDT jobs
                    if envvar_name in os.environ:
                        del os.environ[envvar_name]
                except NameError:
                    logger.debug(
                        f"Variable name '{env_var.get('name')}' is not defined"
                    )

        # refresh environment to update variables
        refresh_environment()

        # log
        logger.debug(f"Job {self.ID} ran successfully.")

    # -- INTERNAL LOGIC ------------------------------------------------------
    def prepare_value(self, value: str, value_type: str | None = None) -> str:
        """Prepare value to be used in the environment variable.

        It performs some checks or operations depending on value type: user and
            variable expansion, check if URL is valid, etc.

        Args:
            value (str): value to prepare.
            value_type (str, optional): type of input value. Defaults to "str".

        Returns:
            str: prepared value.
        """

        if value_type == "url":
            if check_str_is_url(input_str=value, raise_error=False):
                logger.info(
                    f"{value} is a valid URL. Using it as environment variable value."
                )
            else:
                logger.warning(
                    f"{value} seems to be an invalid URL. It will be applied anyway."
                )

            return value.strip()
        elif value_type in ("bool", "str"):
            return str(value).strip()
        elif value_type == "path":
            # test if value is a path
            if check_var_can_be_path(input_var=value, raise_error=False):
                value_as_path = Path(expanduser(expandvars(value)))  # noqa: PTH111
                if not check_path_exists(input_path=value_as_path, raise_error=False):
                    logger.warning(
                        f"{value} seems to be a valid path but does not exist (yet)."
                    )
                return str(Path(value_as_path).resolve())
            else:
                logger.debug(
                    f"Value {value} is not a valid path. The raw string will be used."
                )

        return str(value).strip()

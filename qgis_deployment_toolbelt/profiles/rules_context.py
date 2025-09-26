#! python3  # noqa: E265

"""
Rules context.

Author: Julien Moura (https://github.com/guts)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import json
import logging
import platform
from datetime import date
from getpass import getuser
from os import _Environ, environ
from sys import platform as opersys
from typing import Any

# package
from qgis_deployment_toolbelt.utils.user_groups import (
    get_user_domain_groups,
    get_user_local_groups,
)
from qgis_deployment_toolbelt.utils.win32utils import (
    ExtendedNameFormat,
    get_current_user_extended_data,
)


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Functions #############
# ##################################


class QdtRulesContext:
    def __init__(
        self,
        only_prefixed_variables: bool = True,
        variables_prefix: list[str] | None = None,
    ) -> None:
        """Initialize a QDT rules context object.

        Args:
            only_prefixed_variables (bool, optional): Option to only list prefixed
            variables. Defaults to True.
            variables_prefix (list[str] | None, optional): List of allowed prefixes.
            Defaults to None.
        """
        self.only_prefixed_variables = only_prefixed_variables

        if variables_prefix is None:
            self.variables_prefix = ["QDT_", "QGIS_"]
        else:
            self.variables_prefix = variables_prefix

    @property
    def _context_date(self) -> dict:
        """Returns a context dictionary with date informations that can be used in QDT
        various places: rules...

        Returns:
            dict: dict with current date informations
        """
        today = date.today()
        return {
            "current_day": today.day,
            "current_weekday": today.weekday(),  # monday = 0, sunday = 6
            "current_month": today.month,
            "current_year": today.year,
        }

    @property
    def _context_env(self) -> dict[str, str] | _Environ[str]:
        """Returns a dictionary containing environment variables that can be used in
            QDT various places: rules...

        The environment variables can be filtered based on self.only_prefixed_variables
        and self.variables_prefix settings.

        Returns:
            dict[str, str] | _Environ[str]: dict with environment variables to use in
            rules
        """

        if self.only_prefixed_variables:
            # Filter variables that start with any of the prefixes
            return {
                key: value
                for key, value in environ.items()
                if any(key.startswith(prefix) for prefix in self.variables_prefix)
            }

        return environ

    @property
    def _context_environment(self) -> dict:
        """Returns a dictionary containing some environment information (computer, network,
            platform) that can be used in QDT various places: rules...

        Returns:
            dict: dict with some environment metadata to use in rules.
        """
        try:
            linux_distribution_name = f"{platform.freedesktop_os_release().get('NAME')}"
            linux_distribution_version = (
                f"{platform.freedesktop_os_release().get('VERSION_ID')}"
            )
        except OSError as err:
            if opersys == "linux":
                logger.debug(
                    f"Unable to determine current Linux distribution. Trace: {err}."
                )
            linux_distribution_name = None
            linux_distribution_version = None

        return {
            "computer_network_name": platform.node(),
            "operating_system_code": opersys,
            "operating_system_release": platform.release(),
            "processor_architecture": platform.machine(),
            # custom Linux
            "linux_distribution_name": linux_distribution_name,
            "linux_distribution_version": linux_distribution_version,
            # custom Windows
            "windows_edition": platform.win32_edition(),
        }

    @property
    def _context_user(self) -> dict:
        """Returns a dictionary containing user informations that can be used in QDT Rules
            context.

        Returns:
            dict: dict user information.
        """
        if opersys == "win32":
            windows_extended = {
                k.name: get_current_user_extended_data(k) for k in ExtendedNameFormat
            }
        else:
            windows_extended = None

        try:
            user_domain_groups = get_user_domain_groups()
        except Exception as err:
            logger.error(f"Unable to retrieve user domain groups. Trace: {err}")
            user_domain_groups = []

        return {
            "name": getuser(),
            "groups_local": get_user_local_groups(),
            "groups_domain": user_domain_groups,
            "windows_extended": windows_extended,
        }

    # -- EXPORT
    def to_dict(self) -> dict:
        """Convert object into dictionary.

        Returns:
            dict: object as dictionary
        """
        result = {}
        for attr in dir(self):
            if isinstance(
                getattr(self.__class__, attr, None), property
            ) and attr.startswith("_context_"):
                result[attr.removeprefix("_context_")] = getattr(self, attr)
        return result

    def to_json(self, **kwargs: Any) -> str:
        """Supersedes json.dumps using the dictionary returned by to_dict().
        kwargs are passed to json.dumps.

        Returns:
            str: object serialized as JSON string

        Example:

            .. code-block:: python

                from pathlib import Path

                rules_context = QdtRulesContext()

                # write into the file passing extra parameters to json.dumps
                with Path("qdt_rules_context.json").open("w", encoding="UTF8") as wf:
                    wf.write(rules_context.to_json(indent=4, sort_keys=True))
        """
        obj_as_dict = self.to_dict()

        return json.dumps(obj_as_dict, **kwargs)

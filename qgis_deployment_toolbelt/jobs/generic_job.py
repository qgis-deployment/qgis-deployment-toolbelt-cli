#! python3  # noqa: E265

"""
Base of QDT jobs.

Author: Julien Moura (https://github.com/guts)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from functools import cached_property
from os import getenv
from pathlib import Path
from typing import Any

# 3rd party
from python_rule_engine import RuleEngine

# package
from qgis_deployment_toolbelt.constants import (
    OSConfiguration,
    get_qdt_working_directory,
)
from qgis_deployment_toolbelt.exceptions import (
    JobOptionBadNameError,
    JobOptionBadValueError,
    JobOptionBadValueTypeError,
)
from qgis_deployment_toolbelt.profiles.qdt_profile import QdtProfile
from qgis_deployment_toolbelt.profiles.rules_context import QdtRulesContext
from qgis_deployment_toolbelt.utils.str2bool import str2bool


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)

# #############################################################################
# ########## Classes ###############
# ##################################


class GenericJob:
    """Generic base for QDT jobs."""

    ID: str = ""
    OPTIONS_SCHEMA: dict[str, dict[str, Any]] = {}

    RULES_FILTER_CACHE: dict[
        tuple[Path, ...], tuple[list[QdtProfile], list[QdtProfile]]
    ] = {}

    def __init__(self) -> None:
        """Object instanciation."""

        # QDT rules context
        only_prefixed_variables = str2bool(
            getenv("QDT_RULES_ONLY_PREFIXED_VARIABLES", "true")
        )
        variables_prefix = getenv("QDT_RULES_VARIABLES_PREFIX", "QDT_,QGIS_").split(",")
        self.qdt_rules_context = QdtRulesContext(
            only_prefixed_variables=only_prefixed_variables,
            variables_prefix=variables_prefix,
        )

        # local QDT folders
        self.qdt_working_folder = get_qdt_working_directory()
        self._ensure_folder_exists(
            folder_path=self.qdt_working_folder, log_label="QDT working folder"
        )
        logger.debug(f"QDT working folder: {self.qdt_working_folder}")

        self.qdt_downloaded_repositories = self.qdt_working_folder.joinpath(
            f"repositories/{getenv('QDT_TMP_RUNNING_SCENARIO_ID', 'default')}"
        )
        logger.debug(
            f"Current scenario repository folder: {self.qdt_downloaded_repositories}"
        )

        self.qdt_plugins_folder = self.qdt_working_folder.joinpath("plugins")
        logger.debug(f"QDT local plugins cache folder: {self.qdt_plugins_folder}")

        # destination profiles folder
        self.qgis_profiles_path: Path = self.os_config.qgis_profiles_path
        if not self.qgis_profiles_path.exists():
            logger.info(
                f"Installed QGIS profiles folder not found: {self.qgis_profiles_path}. "
                "Creating it to properly run the job."
            )
            self.qgis_profiles_path.mkdir(parents=True)
        logger.debug(f"Installed QGIS profiles folder: {self.qgis_profiles_path}")

    # -- Properties
    @cached_property
    def os_config(self) -> OSConfiguration:
        """Get current operating system configuration.

        Returns:
            OSConfiguration: object with settings regarding operating system and QGIS
        """
        return OSConfiguration.from_opersys()

    # -- Methods
    def list_downloaded_profiles(self) -> tuple[QdtProfile] | None:
        """List downloaded QGIS profiles, i.e. a profile's folder located into the QDT
            working folder.
            Typically: `~/.cache/qgis-deployment-toolbelt/repositories/geotribu` or
            `%USERPROFILE%/.cache/qgis-deployment-toolbelt/repositories/geotribu`).

        Returns:
            tuple[QdtProfile] | None: tuple of profiles objects or None if no profile
                folder listed
        """
        return self.filter_profiles_folder(
            start_parent_folder=self.qdt_downloaded_repositories
        )

    def list_installed_profiles(self) -> tuple[QdtProfile] | None:
        """List installed QGIS profiles, i.e. a profile's folder located into the QGIS
            profiles path and so accessible to the end-user through the QGIS interface.
            Typically: `~/.local/share/QGIS/QGIS3/profiles/geotribu` or
            `%APPDATA%/QGIS/QGIS3/profiles/geotribu`).

        Returns:
            tuple[QdtProfile] | None: tuple of profiles objects or None if no profile is
                installed in QGIS3/profiles
        """
        return self.filter_profiles_folder(start_parent_folder=self.qgis_profiles_path)

    def filter_profiles_folder(
        self, start_parent_folder: Path
    ) -> tuple[QdtProfile, ...] | None:
        """Parse a folder structure to filter on QGIS profiles folders.

        Returns:
            tuple[QdtProfile] | None: tuple of profiles objects matching criteria or
                None if no profile folder found
        """
        # first, try to get folders containing a profile.json
        li_qgis_qdt_profiles: list[QdtProfile] = [
            QdtProfile.from_json(profile_json_path=f, profile_folder=f.parent)
            for f in start_parent_folder.glob("**/profile.json")
        ]

        if not len(li_qgis_qdt_profiles):
            logger.error(f"No QGIS profile found in {start_parent_folder}.")
            return

        logger.debug(
            f"{len(li_qgis_qdt_profiles)} profiles found within {start_parent_folder}"
        )

        # filter out profiles that do not match the rules
        profiles_matched, profiles_unmatched = self.filter_profiles_on_rules(
            tup_qdt_profiles=tuple(li_qgis_qdt_profiles)
        )

        if not len(profiles_matched):
            logger.warning(
                f"None of the {len(li_qgis_qdt_profiles)} profiles meet the deployment "
                "requirements."
            )
            return

        if len(profiles_unmatched):
            logger.info(
                f"{len(profiles_unmatched)}/{len(li_qgis_qdt_profiles)} profiles "
                "do not meet the conditions for deployment: "
                f"{', '.join([p.name for p in profiles_unmatched])}"
            )

        return tuple(profiles_matched)

    def get_matching_profile_from_name(
        self, li_profiles: list[QdtProfile], profile_name: str
    ) -> QdtProfile:
        """Get a profile from list of profiles using a profile's name to match.

        Args:
            li_profiles (list[QdtProfile]): list of profile to look into
            profile_name (str): profile name

        Returns:
            QdtProfile: matching profile object
        """
        # load profile
        matching_qdt_profile = [
            pr for pr in li_profiles if profile_name in (pr.name, pr.folder.name)
        ]
        if not len(matching_qdt_profile):
            logger.error(
                "Unable to get a matching profile among downloaded ones with "
                f"the name: {profile_name}"
            )
            return None

        qdt_profile = matching_qdt_profile[0]
        logger.info(
            f"Downloaded profile matched: {qdt_profile.name} from {qdt_profile.folder}"
        )
        return qdt_profile

    def filter_profiles_on_rules(
        self, tup_qdt_profiles: tuple[QdtProfile, ...], cached: bool = True
    ) -> tuple[list[QdtProfile], list[QdtProfile]]:
        """Evaluate profile regarding to its deployment rules. Results are stored in
        the class ``RULES_FILTER_CACHE`` attribute.

        Args:
            tup_qdt_profiles (tuple[QdtProfile, ...]): input tuple of QDT profiles
            cached (bool, optional): using previously computed value if not None.
                Defaults to True.

        Returns:
            tuple[QdtProfile], list[QdtProfile]]: tuple of profiles that matched
            and those which did not match their deployment rules
        """
        # check previous cached result
        cache_key: tuple[Path, ...] = tuple(
            p.folder for p in tup_qdt_profiles if isinstance(p.folder, Path)
        )
        if cached:
            if cache_key in self.RULES_FILTER_CACHE:
                logger.debug(
                    f"Profiles '{cache_key}' have "
                    "already been evaluated, returning previous result. "
                    "Use 'cached=False' to force re-checking."
                )
                return self.RULES_FILTER_CACHE[cache_key]
            logger.debug(
                f"Profiles '{cache_key}' have not been evaluated yet, checking rules..."
            )
        else:
            logger.debug("Profiles rules evaluation forced, checking rules...")

        # local vars
        li_profiles_matched: list[QdtProfile] = []
        li_profiles_unmatched: list[QdtProfile] = []
        rules_context = self.qdt_rules_context.to_dict()

        # checking each profile against rules
        for profile in tup_qdt_profiles:
            if profile.rules is None:
                logger.debug(f"No rules to apply to {profile.name}")
                li_profiles_matched.append(profile)
                continue

            logger.debug(
                f"Checking that profile '{profile.name}' matches deployment conditions. "
                f"{len(profile.rules)} rules found."
            )
            try:
                engine = RuleEngine(rules=profile.rules)
                results = engine.evaluate(obj=rules_context)
                if len(results) == len(profile.rules):
                    logger.debug(
                        f"Profile '{profile.name}' matches {len(profile.rules)} "
                        "deployment rule(s)."
                    )
                    li_profiles_matched.append(profile)
                else:
                    logger.info(
                        f"Profile '{profile.name}' does not match the deployment "
                        f"conditions: {len(results)}/{len(profile.rules)} rule(s) "
                        "matched."
                    )
                    li_profiles_unmatched.append(profile)

            except Exception as err:
                logger.error(
                    f"Error occurred parsing rules of profile '{profile.name}'. "
                    f"Trace: {err}"
                )

        # store result for other jobs that would need it later
        self.RULES_FILTER_CACHE[cache_key] = (
            li_profiles_matched,
            li_profiles_unmatched,
        )
        return li_profiles_matched, li_profiles_unmatched

    def validate_options(self, options: dict[str, Any]) -> dict[str, Any]:
        """Validate job options against ``OPTIONS_SCHEMA``.

        Args:
            options (dict[str, Any]): options to validate

        Raises:
            JobOptionBadNameError: if an option name is not in the schema
            JobOptionBadValueError: if an option value fails its condition
            JobOptionBadValueTypeError: if an option value has the wrong type
            TypeError: if options is not a dict

        Returns:
            dict[str, Any]: unchanged when all checks pass
        """
        if not isinstance(options, dict):
            raise TypeError(f"Options to validate must be a dict, not {type(options)}.")

        for option_name, option_value in options.items():
            if option_name not in self.OPTIONS_SCHEMA:
                raise JobOptionBadNameError(
                    job_id=self.ID,
                    bad_option_name=option_name,
                    expected_options_names=self.OPTIONS_SCHEMA.keys(),
                )

            option_def: dict[str, Any] = self.OPTIONS_SCHEMA[option_name]

            # check value type
            if not isinstance(option_value, option_def["type"]):
                raise JobOptionBadValueTypeError(
                    job_id=self.ID,
                    bad_option_name=option_name,
                    bad_option_value=option_value,
                    expected_option_type=option_def["type"],
                )

            # check value condition
            option_condition: str | None = option_def.get("condition")
            option_possible_values: tuple[str, ...] | None = option_def.get(
                "possible_values"
            )

            if option_condition == "startswith" and not option_value.startswith(
                option_possible_values
            ):
                raise JobOptionBadValueError(
                    job_id=self.ID,
                    bad_option_name=option_name,
                    bad_option_value=option_value,
                    condition="startswith",
                    accepted_values=option_possible_values,
                )
            elif (
                option_condition == "in" and option_value not in option_possible_values
            ):
                raise JobOptionBadValueError(
                    job_id=self.ID,
                    bad_option_name=option_name,
                    bad_option_value=option_value,
                    condition="in",
                    accepted_values=option_def.get("possible_values"),
                )
            else:
                pass

        return options

    # -- Utils
    def _ensure_folder_exists(
        self, folder_path: Path, log_label: str | None = None
    ) -> None:
        """Create folder and its parents when it does not exist yet.

        Args:
            folder_path (Path): pat to directory to create if absent.
            log_label (str | None, optional): human-readable name used in the log message. Defaults to None
        """
        if not folder_path.exists():
            msg_display = log_label or str(folder_path)
            logger.debug(
                f"{msg_display} not found: {folder_path}. Creating it to properly run the job."
            )
            folder_path.mkdir(parents=True, exist_ok=True)

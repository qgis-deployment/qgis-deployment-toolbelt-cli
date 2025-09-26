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
from functools import lru_cache
from os import getenv
from pathlib import Path

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
    OPTIONS_SCHEMA: dict[dict] = dict(dict())

    def __init__(self) -> None:
        """Object instanciation."""
        # operating system configuration
        self.os_config = OSConfiguration.from_opersys()

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
        if not self.qdt_working_folder.exists():
            logger.info(
                f"QDT downloaded folder not found: {self.qdt_working_folder}. "
                "Creating it to properly run the job."
            )
            self.qdt_working_folder.mkdir(parents=True, exist_ok=True)
        logger.debug(f"QDT working folder: {self.qdt_working_folder}")

        self.qdt_downloaded_repositories = self.qdt_working_folder.joinpath(
            f"repositories/{getenv('QDT_TMP_RUNNING_SCENARIO_ID', 'default')}"
        )
        self.qdt_plugins_folder = self.qdt_working_folder.joinpath("plugins")

        # destination profiles folder
        self.qgis_profiles_path: Path = self.os_config.qgis_profiles_path
        if not self.qgis_profiles_path.exists():
            logger.info(
                f"Installed QGIS profiles folder not found: {self.qgis_profiles_path}. "
                "Creating it to properly run the job."
            )
            self.qgis_profiles_path.mkdir(parents=True)
        logger.debug(f"Installed QGIS profiles folder: {self.qgis_profiles_path}")

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

    @lru_cache(maxsize=1024)  # noqa: B019
    def filter_profiles_on_rules(
        self, tup_qdt_profiles: tuple[QdtProfile]
    ) -> tuple[list[QdtProfile], list[QdtProfile]]:
        """Evaluate profile regarding to its deployment rules.

        Args:
            tup_qdt_profiles (tuple[QdtProfile]): input tuple of QDT profiles

        Returns:
            tuple[list[QdtProfile], list[QdtProfile]]: tuple of profiles that matched
            and those which did not match their deployment rules
        """
        li_profiles_matched = []
        li_profiles_unmatched = []

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
                results = engine.evaluate(obj=self.qdt_rules_context.to_dict())
                if len(results) == len(profile.rules):
                    logger.debug(
                        f"Profile '{profile.name}' matches {len(profile.rules)} deployment rule(s)."
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
                    f"Error occurred parsing rules of profile '{profile.name}'. Trace: {err}"
                )

        return li_profiles_matched, li_profiles_unmatched

    def validate_options(self, options: dict[dict]) -> dict[dict]:
        """Validate options.

        Args:
            options (dict[dict]): options to validate.

        Raises:
            ValueError: if option has an invalid name or doesn't comply with condition
            TypeError: if the option does'nt not comply with expected type

        Returns:
            dict[dict]: options if valid
        """
        if not isinstance(options, dict):
            raise TypeError(f"Options to validate must be a dict, not {type(options)}.")

        for option in options:
            if option not in self.OPTIONS_SCHEMA:
                raise JobOptionBadNameError(
                    job_id=self.ID,
                    bad_option_name=option,
                    expected_options_names=self.OPTIONS_SCHEMA.keys(),
                )

            option_in = options.get(option)
            option_def: dict = self.OPTIONS_SCHEMA.get(option)
            # check value type
            if not isinstance(option_in, option_def.get("type")):
                raise JobOptionBadValueTypeError(
                    job_id=self.ID,
                    bad_option_name=option,
                    bad_option_value=option_in,
                    expected_option_type=option_def.get("type"),
                )
            # check value condition
            if option_def.get("condition") == "startswith" and not option_in.startswith(
                option_def.get("possible_values")
            ):
                raise JobOptionBadValueError(
                    job_id=self.ID,
                    bad_option_name=option,
                    bad_option_value=option_in,
                    condition="startswith",
                    accepted_values=option_def.get("possible_values"),
                )
            elif option_def.get(
                "condition"
            ) == "in" and option_in not in option_def.get("possible_values"):
                raise JobOptionBadValueError(
                    job_id=self.ID,
                    bad_option_name=option,
                    bad_option_value=option_in,
                    condition="startswith",
                    accepted_values=option_def.get("possible_values"),
                )
            else:
                pass

        return options

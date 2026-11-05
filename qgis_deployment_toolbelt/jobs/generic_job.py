#! python3  # noqa: E265

"""
Base of QDT jobs.

Author: Julien Moura (https://github.com/guts)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import json
import logging
from abc import ABC, abstractmethod
from functools import cached_property
from os import getenv
from pathlib import Path
from typing import Any

# 3rd party
from python_rule_engine import RuleEngine

# package
from qgis_deployment_toolbelt.constants import (
    ENV_VAR_QGIS_VERSION,
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
from qgis_deployment_toolbelt.reports import CleanupReport
from qgis_deployment_toolbelt.utils.str2bool import str2bool


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)

# #############################################################################
# ########## Classes ###############
# ##################################


class GenericJob(ABC):
    """Abstract base for QDT jobs.

    It provides the shared context (QDT working folders, QGIS profiles folder,
    operating system configuration, rules context) and helpers to list profiles and
    validate options. A concrete job must define:

    - ``ID``, the identifier used in the ``uses`` key of a scenario step;
    - ``OPTIONS_SCHEMA``, the options accepted in the ``with`` key, checked by
      :meth:`validate_options`;
    - :meth:`run`, called by the deployment command once the job is instantiated.

    ``ID`` and ``OPTIONS_SCHEMA`` are declared as abstract properties so that a
    plain class attribute in the subclass implements them.

    Example:
        .. code-block:: python

            class JobExample(GenericJob):
                ID: str = "example-job"
                OPTIONS_SCHEMA: dict = {}

                def __init__(self, options: dict) -> None:
                    super().__init__()
                    self.options: dict = self.validate_options(options)

                def run(self) -> None: ...

    """

    ENSURE_QGIS_PROFILES_FOLDER: bool = True

    # -- CACHE --
    PROFILES_FOLDER_CACHE: dict[Path, tuple[QdtProfile, ...] | None] = {}
    RULES_FILTER_CACHE: dict[str, bool | None] = {}

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
        if self.ENSURE_QGIS_PROFILES_FOLDER:
            self._ensure_folder_exists(
                folder_path=self.qgis_profiles_path,
                log_label="Installed QGIS profiles folder",
            )
        logger.debug(
            f"Installed QGIS {self.os_config.qgis_version_major} profiles folder: "
            f"{self.qgis_profiles_path}"
        )

    # -- Cache management
    @classmethod
    def clear_profiles_cache(cls, folder_path: Path | None = None) -> None:
        """Invalidate the profiles-folder scan cache to make subsequent jobs re-scan
        the directory instead of returning cached data.

        Args:
            folder_path (Path | None, optional): specific cached folder to clear.
                If None, the entire cache is cleared.  Defaults to None.
        """
        if folder_path is None:
            to_be_cleared = len(cls.PROFILES_FOLDER_CACHE)
            cls.PROFILES_FOLDER_CACHE.clear()
            logger.debug(f"{to_be_cleared} profiles folder cache cleared.")
        elif folder_path in cls.PROFILES_FOLDER_CACHE:
            del cls.PROFILES_FOLDER_CACHE[folder_path]
            logger.debug(f"Profiles folder cache entry evicted for: {folder_path}")

    # -- Properties
    @cached_property
    def os_config(self) -> OSConfiguration:
        """Get current operating system configuration.

        Returns:
            OSConfiguration: object with settings regarding operating system and QGIS
        """
        return OSConfiguration.from_opersys()

    # -- Members to be implemented by concrete jobs
    @property
    @abstractmethod
    def ID(self) -> str:  # noqa: N802
        """Job identifier, used in the ``uses`` key of a scenario step."""
        raise NotImplementedError(f"{type(self).__name__} must define ID.")

    @property
    @abstractmethod
    def OPTIONS_SCHEMA(self) -> dict[str, dict[str, Any]]:  # noqa: N802
        """Options accepted in the ``with`` key of a scenario step."""
        raise NotImplementedError(f"{type(self).__name__} must define OPTIONS_SCHEMA.")

    @abstractmethod
    def run(self) -> CleanupReport | None:
        """Execute the job logic. Must be implemented by every concrete job."""
        raise NotImplementedError(f"{type(self).__name__} must define run.")

    # -- Shared methods
    def list_downloaded_profiles(
        self, quiet: bool = False
    ) -> tuple[QdtProfile, ...] | None:
        """List downloaded QGIS profiles, i.e. a profile's folder located into the QDT
            working folder.
            Typically: `~/.cache/qgis-deployment-toolbelt/repositories/geotribu` or
            `%USERPROFILE%/.cache/qgis-deployment-toolbelt/repositories/geotribu`).

        Args:
            quiet (bool, optional): if True, log the "no profile found" case as debug
                instead of error. Useful for lookups where an empty result is an
                expected outcome, not a failure. Defaults to False.

        Returns:
            tuple[QdtProfile, ...] | None: tuple of profiles objects or None if no profile
                folder listed
        """
        return self.filter_profiles_folder(
            start_parent_folder=self.qdt_downloaded_repositories, quiet=quiet
        )

    def list_installed_profiles(
        self, quiet: bool = False
    ) -> tuple[QdtProfile, ...] | None:
        """List installed QGIS profiles, i.e. a profile's folder located into the QGIS
            profiles path and so accessible to the end-user through the QGIS interface.
            Typically: `~/.local/share/QGIS/QGIS4/profiles/geotribu` or
            `%APPDATA%/QGIS/QGIS3/profiles/geotribu`).

        Args:
            quiet (bool, optional): if True, log the "no profile found" case as debug
                instead of error. Useful for lookups where an empty result is an
                expected outcome, not a failure. Defaults to False.

        Returns:
            tuple[QdtProfile, ...] | None: tuple of profiles objects or None if no profile is
                installed in the QGIS profiles folder
        """
        return self.filter_profiles_folder(
            start_parent_folder=self.qgis_profiles_path, quiet=quiet
        )

    def read_profiles_folder(self, start_parent_folder: Path) -> tuple[QdtProfile, ...]:
        """Read a folder structure to list every QGIS profile handled by QDT,
            without applying any of the deployment filters (QDT version,
            deprecation, deployment rules).

        Args:
            start_parent_folder (Path): root directory to scan for profile.json
                files.

        Returns:
            tuple[QdtProfile, ...]: tuple of profiles objects found under the
                folder. Empty if the folder does not exist or contains no profile.
        """
        if not start_parent_folder.is_dir():
            logger.debug(f"Folder to scan does not exist: {start_parent_folder}")
            return ()

        return tuple(
            QdtProfile.from_json(profile_json_path=f, profile_folder=f.parent)
            for f in start_parent_folder.glob("**/profile.json")
        )

    def filter_profiles_folder(
        self, start_parent_folder: Path, cached: bool = True, quiet: bool = False
    ) -> tuple[QdtProfile, ...] | None:
        """Parse a folder structure to filter on QGIS profiles folders.

        Args:
            start_parent_folder (Path): root directory to scan for profile.json files.
            cached (bool, optional): return the previously computed result when available.
                Defaults to True.
            quiet (bool, optional): if True, log the "no profile found" case as debug
                instead of error. Set this when an empty folder is an expected outcome
                rather than a failure condition for the calling job. Defaults to False.

        Returns:
            tuple[QdtProfile, ...] | None: tuple of profiles objects matching criteria or
                None if no profile folder found
        """
        if cached and start_parent_folder in self.PROFILES_FOLDER_CACHE:
            logger.debug(
                f"Returning cached profiles for {start_parent_folder} "
                "(use cached=False to force re-scan)."
            )
            return self.PROFILES_FOLDER_CACHE[start_parent_folder]

        # first, try to get folders containing a profile.json
        li_qgis_qdt_profiles: list[QdtProfile] = list(
            self.read_profiles_folder(start_parent_folder=start_parent_folder)
        )

        if not len(li_qgis_qdt_profiles):
            log_method = logger.debug if quiet else logger.error
            log_method(
                f"No QGIS profile managed by QDT found in {start_parent_folder}."
            )
            self.PROFILES_FOLDER_CACHE[start_parent_folder] = None
            return

        logger.debug(
            f"{len(li_qgis_qdt_profiles)} profiles found within {start_parent_folder}"
        )

        # filter out profiles incompatible with the running QDT version
        profiles_version_ok, _ = self.filter_profiles_on_qdt_version(
            tup_qdt_profiles=tuple(li_qgis_qdt_profiles)
        )

        if not len(profiles_version_ok):
            logger.warning(
                f"None of the {len(li_qgis_qdt_profiles)} profiles are compatible "
                "with the running QDT version."
            )
            self.PROFILES_FOLDER_CACHE[start_parent_folder] = None
            return

        # filter out profiles flagged as deprecated
        profiles_active, profiles_deprecated = self.filter_profiles_on_deprecated_flag(
            tup_qdt_profiles=tuple(profiles_version_ok)
        )
        if profiles_deprecated:
            logger.info(
                f"{len(profiles_deprecated)} profile(s) flagged as deprecated won't "
                f"be deployed: {', '.join(p.name for p in profiles_deprecated)}"
            )

        if not profiles_active:
            logger.warning("No profile left to deploy once deprecated ones excluded.")
            self.PROFILES_FOLDER_CACHE[start_parent_folder] = None
            return

        # filter out profiles incompatible with the targeted QGIS version
        profiles_compatible_qgis, _ = self.filter_profiles_on_qgis_version(
            tup_qdt_profiles=tuple(profiles_active)
        )
        if not profiles_compatible_qgis:
            logger.warning(
                f"None of the {len(profiles_active)} profiles are compatible "
                "with the targeted QGIS version."
            )
            self.PROFILES_FOLDER_CACHE[start_parent_folder] = None
            return

        # filter out profiles that do not match the rules
        profiles_matched, profiles_unmatched = self.filter_profiles_on_rules(
            tup_qdt_profiles=tuple(profiles_compatible_qgis)
        )

        if not len(profiles_matched):
            logger.warning(
                f"None of the {len(li_qgis_qdt_profiles)} profiles meet the deployment "
                "requirements."
            )
            self.PROFILES_FOLDER_CACHE[start_parent_folder] = None
            return

        if len(profiles_unmatched):
            logger.info(
                f"{len(profiles_unmatched)}/{len(li_qgis_qdt_profiles)} profiles "
                "do not meet the conditions for deployment: "
                f"{', '.join([p.name for p in profiles_unmatched])}"
            )

        # consolide listing result and cache them for later use
        tup_profiles_matched = tuple(profiles_matched)
        self.PROFILES_FOLDER_CACHE[start_parent_folder] = tup_profiles_matched
        return tup_profiles_matched

    def get_matching_profile_from_name(
        self, li_profiles: list[QdtProfile], profile_name: str
    ) -> QdtProfile | None:
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

    # -- Filtering profiles lists --
    def filter_profiles_on_deprecated_flag(
        self, tup_qdt_profiles: tuple[QdtProfile, ...]
    ) -> tuple[list[QdtProfile], list[QdtProfile]]:
        """Evaluate profiles against their optional `deprecated` attribute.

        Args:
            tup_qdt_profiles (tuple[QdtProfile, ...]): input tuple of QDT profiles

        Returns:
            tuple[list[QdtProfile], list[QdtProfile]]: tuple of profiles that are
            active (not deprecated) and those which are deprecated
        """
        li_profiles_active: list[QdtProfile] = []
        li_profiles_deprecated: list[QdtProfile] = []

        for profile in tup_qdt_profiles:
            if profile.is_deprecated:
                li_profiles_deprecated.append(profile)
            else:
                li_profiles_active.append(profile)

        return li_profiles_active, li_profiles_deprecated

    def filter_profiles_on_qdt_version(
        self, tup_qdt_profiles: tuple[QdtProfile, ...]
    ) -> tuple[list[QdtProfile], list[QdtProfile]]:
        """Evaluate profiles against their optional `qdtMinVersion` attribute.

        Args:
            tup_qdt_profiles (tuple[QdtProfile, ...]): input tuple of QDT profiles

        Returns:
            tuple[list[QdtProfile], list[QdtProfile]]: tuple of profiles that are
            compatible with the running QDT version and those which are not
        """
        li_profiles_compatible: list[QdtProfile] = []
        li_profiles_incompatible: list[QdtProfile] = []

        for profile in tup_qdt_profiles:
            is_compatible, error_message = profile.is_qdt_version_compatible()
            if is_compatible is False:
                logger.error(error_message)
                li_profiles_incompatible.append(profile)
                continue

            # is_compatible is None: qdtMinVersion could not be parsed
            if is_compatible is None:
                logger.warning(error_message)
            li_profiles_compatible.append(profile)

        return li_profiles_compatible, li_profiles_incompatible

    def filter_profiles_on_qgis_version(
        self, tup_qdt_profiles: tuple[QdtProfile, ...], qgis_version: str | None = None
    ) -> tuple[list[QdtProfile], list[QdtProfile]]:
        """Evaluate profiles against their optional `qgisMinimumVersion` and
        `qgisMaximumVersion` attributes.

        Args:
            tup_qdt_profiles (tuple[QdtProfile, ...]): input tuple of QDT profiles
            qgis_version (str | None, optional): targeted QGIS version. If None, the
                `QDT_QGIS_VERSION` environment variable (set by the job
                `qgis-installation-finder`) is used. Defaults to None.

        Returns:
            tuple[list[QdtProfile], list[QdtProfile]]: tuple of profiles that are
            compatible with the targeted QGIS version (or could not be evaluated) and
            those which are not
        """
        qgis_version = qgis_version or getenv(ENV_VAR_QGIS_VERSION)
        if not qgis_version:
            logger.info(
                "Profiles are not filtered on their QGIS version bounds: the targeted "
                f"QGIS version is unknown ('{ENV_VAR_QGIS_VERSION}' is not set). Run "
                "the 'qgis-installation-finder' job first in the scenario."
            )
            return list(tup_qdt_profiles), []

        li_profiles_compatible: list[QdtProfile] = []
        li_profiles_incompatible: list[QdtProfile] = []

        for profile in tup_qdt_profiles:
            is_compatible, message = profile.is_qgis_version_compatible(
                qgis_version=qgis_version
            )
            if is_compatible is False:
                logger.info(f"{message} It won't be deployed.")
                li_profiles_incompatible.append(profile)
                continue

            # is_compatible is None: a version could not be parsed
            if is_compatible is None:
                logger.warning(message)
            li_profiles_compatible.append(profile)

        return li_profiles_compatible, li_profiles_incompatible

    def filter_profiles_on_rules(
        self, tup_qdt_profiles: tuple[QdtProfile, ...], cached: bool = True
    ) -> tuple[list[QdtProfile], list[QdtProfile]]:
        """Evaluate profiles regarding to their deployment rules.

        Results stored in the class ``RULES_FILTER_CACHE`` attribute, keyed by the
        serialized rules to be shared between jobs. A profile whose rules changed on
        disk is evaluated again.

        Args:
            tup_qdt_profiles (tuple[QdtProfile, ...]): input tuple of QDT profiles
            cached (bool, optional): using previously computed value if not None.
                Defaults to True.

        Returns:
            tuple[list[QdtProfile], list[QdtProfile]]: profiles that matched and
                those which did not match their deployment rules. Profiles whose
                rules could not be evaluated are in none of them.
        """
        li_profiles_matched: list[QdtProfile] = []
        li_profiles_unmatched: list[QdtProfile] = []

        for profile in tup_qdt_profiles:
            if profile.rules is None:
                logger.debug(f"No rules to apply to {profile.name}")
                li_profiles_matched.append(profile)
                continue

            cache_key = json.dumps(profile.rules, sort_keys=True, default=str)
            if cached and cache_key in self.RULES_FILTER_CACHE:
                logger.debug(
                    f"Rules of profile '{profile.name}' have already been evaluated, "
                    "reusing previous result. Use 'cached=False' to force re-checking."
                )
                filter_result = self.RULES_FILTER_CACHE[cache_key]
            else:
                filter_result = self._evaluate_profile_rules(profile=profile)
                self.RULES_FILTER_CACHE[cache_key] = filter_result

            if filter_result is None:
                logger.warning(
                    f"Profile '{profile.name}' is ignored: its deployment rules could "
                    "not be evaluated."
                )
            elif filter_result:
                li_profiles_matched.append(profile)
            else:
                li_profiles_unmatched.append(profile)

        return li_profiles_matched, li_profiles_unmatched

    def _evaluate_profile_rules(self, profile: QdtProfile) -> bool | None:
        """Evaluate the deployment rules of a profile against the rules context.

        Args:
            profile (QdtProfile): profile with rules to evaluate

        Returns:
            bool | None: True if every rule matches, False otherwise. None if the
                rules could not be evaluated.
        """
        logger.debug(
            f"Checking that profile '{profile.name}' matches deployment conditions. "
            f"{len(profile.rules)} rules found."
        )
        try:
            engine = RuleEngine(rules=profile.rules)
            results = engine.evaluate(obj=self.qdt_rules_context.to_dict())
        except Exception as err:
            logger.error(
                f"Deployment rules of profile '{profile.name}' could not be "
                f"evaluated. {type(err).__name__}: {err.__cause__ or err}"
            )
            return None

        if len(results) == len(profile.rules):
            logger.debug(
                f"Profile '{profile.name}' matches {len(profile.rules)} "
                "deployment rule(s)."
            )
            return True

        logger.info(
            f"Profile '{profile.name}' does not match the deployment "
            f"conditions: {len(results)}/{len(profile.rules)} rule(s) matched."
        )
        return False

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
            # check if the value starts with a specific string
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
            # check if the value is in a closed set of possible values
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
            # check if all values are in a closed set of possible values
            elif option_condition == "all_in":
                if not all(item in option_possible_values for item in option_value):
                    raise JobOptionBadValueError(
                        job_id=self.ID,
                        bad_option_name=option_name,
                        bad_option_value=option_value,
                        condition="all_in",
                        accepted_values=option_def.get("possible_values"),
                    )

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

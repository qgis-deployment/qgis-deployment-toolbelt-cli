#! python3  # noqa: E265

"""
Set the default profile in profiles.ini file.

Author: Nicolas Godet (https://github.com/nicogodet)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging

# package
from qgis_deployment_toolbelt.jobs.generic_job import GenericJob
from qgis_deployment_toolbelt.utils.ini_parser_with_path import CustomConfigParser


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################


class JobDefaultProfileSetter(GenericJob):
    """
    Job to set the default profile in profile.ini file.
    """

    ID: str = "default-profile-setter"
    OPTIONS_SCHEMA: dict = {
        "profile": {
            "type": str,
            "required": True,
            "default": None,
            "possible_values": None,
            "condition": None,
        },
        "force_profile_selection_policy": {
            "type": bool | int,
            "required": False,
            "default": None,
            "possible_values": (None, 0, 1, 2, True, False),
            "condition": None,
        },
    }

    def __init__(self, options: dict) -> None:
        """Instantiate the class.

        Args:
            options (List[dict]): list of dictionary with environment variables to set
            or remove.
        """
        super().__init__()
        self.options: dict = self.validate_options(options)

    def run(self) -> None:
        """Execute job logic."""
        # check of there are some profiles folders within the installed folder
        installed_profiles = self.list_installed_profiles()
        if installed_profiles is None:
            logger.error("No QGIS profile found in the installed folder.")
            return

        # check if the provided profile name exists in the installed profiles
        qdt_profile = self.get_matching_profile_from_name(
            li_profiles=installed_profiles,
            profile_name=self.options.get("profile"),
        )
        if not qdt_profile:
            logger.error("No QGIS profile matching the provided profile name.")
            return

        if isinstance(self.options.get("force_profile_selection_policy"), bool):
            logger.warning(
                "The option force_profile_selection_policy should be an integer (0, 1 or 2). "
                "It will be converted to int."
            )
            self.options["force_profile_selection_policy"] = int(
                self.options.get("force_profile_selection_policy")
            )

        selection_policy = self.options.get("force_profile_selection_policy")

        ini_profiles_path = self.qgis_profiles_path / "profiles.ini"

        # check if the profiles.ini file exists and create it with default profile set
        # if not
        if not ini_profiles_path.exists():
            logger.warning(
                "Configuration file profiles.ini doesn't exist. "
                "It will be created but maybe it was not the expected behavior."
            )
            ini_profiles_path.touch(exist_ok=True)
            data = f"[core]\ndefaultProfile={self.options.get('profile')}"
            if selection_policy is not None:
                data += f"\nselectionPolicy={selection_policy}"
            ini_profiles_path.write_text(
                data=data,
                encoding="UTF8",
            )
            logger.info(f"Default profile set to {self.options.get('profile')}")
            logger.debug(f"Job {self.ID} ran successfully.")
            return

        ini_profiles = CustomConfigParser()
        ini_profiles.optionxform = str
        ini_profiles.read(self.qgis_profiles_path / "profiles.ini", encoding="UTF8")

        # set the default profile
        if not ini_profiles.has_section("core"):
            ini_profiles.add_section("core")

        ini_profiles.set("core", "defaultProfile", self.options.get("profile"))
        if selection_policy is not None:
            if (
                ini_profiles.has_option("core", "selectionPolicy")
                and ini_profiles.getint("core", "selectionPolicy") != selection_policy
            ):
                logger.info(
                    "The selection policy is already set in the profiles.ini file. "
                    f"It will be overridden from {ini_profiles.getint('core', 'selectionPolicy')} to {selection_policy}."
                )
            elif not ini_profiles.has_option("core", "selectionPolicy"):
                logger.info(
                    "The selection policy is not set in the profiles.ini file. "
                    f"It will be set to {selection_policy}."
                )
            ini_profiles.set("core", "selectionPolicy", str(selection_policy))

        with ini_profiles_path.open("w", encoding="UTF8") as wf:
            ini_profiles.write(wf, space_around_delimiters=False)
            logger.info(f"Default profile set to {self.options.get('profile')}")

        logger.debug(f"Job {self.ID} ran successfully.")

#! python3  # noqa: E265

"""
Download remote QGIS profiles to QDT working folder.

Author: Julien Moura (https://github.com/guts)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging

# package
from qgis_deployment_toolbelt.jobs.generic_job import GenericJob
from qgis_deployment_toolbelt.profiles import LocalGitHandler, RemoteGitHandler
from qgis_deployment_toolbelt.profiles.remote_http_handler import HttpHandler


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################


class JobProfilesDownloader(GenericJob):
    """
    Job to download remote profiles and set them.
    """

    ID: str = "qprofiles-downloader"
    OPTIONS_SCHEMA: dict = {
        "branch": {
            "type": str,
            "required": False,
            "default": "master",
            "possible_values": None,
            "condition": None,
        },
        "protocol": {
            "type": str,
            "required": True,
            "default": "git_remote",
            "possible_values": ("git", "git_local", "git_remote", "http"),
            "condition": "in",
        },
        "source": {
            "type": str,
            "required": True,
            "default": None,
            "possible_values": ("https://", "http://", "git://", "file://"),
            "condition": "startswith",
        },
    }
    PROFILES_NAMES_DOWNLOADED: list = []

    def __init__(self, options: dict) -> None:
        """Instantiate the class.

        Args:
            options (List[dict]): list of dictionary with environment variables to set
            or remove.
        """
        super().__init__()
        self.options: dict = self.validate_options(options)

        # where QDT downloads remote repositories
        self.qdt_downloaded_repositories.mkdir(exist_ok=True, parents=True)
        logger.debug(f"Local repositories folder: {self.qdt_downloaded_repositories}")

    def run(self) -> None:
        """Execute job logic."""
        # prepare remote source
        if self.options.get("protocol") in ("git", "git_local", "git_remote"):
            if self.options.get("protocol") == "git":
                logger.warning(
                    DeprecationWarning(
                        "'git' protocol has been split into 2 more explicit: 'git_local' "
                        "(for git repositories accessible directly through file system "
                        "and 'git_remote' (for repositories accessible network request "
                        "to a remote git server through HTTP). "
                        "Please update your scenario consequently."
                    )
                )
            if self.options.get("protocol") == "git_remote" or self.options.get(
                "source"
            ).startswith(("git://", "http://", "https://")):
                downloader = RemoteGitHandler(
                    source_repository_url=self.options.get("source"),
                    branch_to_use=self.options.get("branch", "master"),
                )
            elif self.options.get("source").startswith("file://"):
                downloader = LocalGitHandler(
                    source_repository_path_or_uri=self.options.get("source"),
                    branch_to_use=self.options.get("branch", "master"),
                )
            else:
                logger.error(
                    f"Source type is not implemented yet: {self.options.get('source')}"
                    f"for '{self.options.get('protocol')}' protocol"
                )
                raise NotImplementedError
        elif self.options.get("protocol") == "http":
            if not self.options.get("source").startswith(("http://", "https://")):
                logger.error(
                    f"Source type not implemented yet: {self.options.get('source')} "
                    f"for '{self.options.get('protocol')}' protocol"
                )
                raise NotImplementedError
            downloader = HttpHandler(
                source_repository_path_or_uri=self.options.get("source"),
            )
        else:
            logger.critical(
                f"Protocol '{self.options.get('protocol')}' is not part of supported ones: "
                f"{self.OPTIONS_SCHEMA.get('protocol').get('possible_values')}"
            )
            raise NotImplementedError

        # run download operation
        downloader.download(destination_local_path=self.qdt_downloaded_repositories)

        # check of there are some profiles folders within the downloaded folder
        profiles_folders = self.list_downloaded_profiles()
        if profiles_folders is None:
            logger.error("No QGIS profile found in the downloaded folder.")
            return

        # store downloaded profiles names
        self.PROFILES_NAMES_DOWNLOADED = [d.name for d in profiles_folders]
        logger.info(
            f"{len(self.PROFILES_NAMES_DOWNLOADED)} downloaded profiles: "
            f"{', '.join(self.PROFILES_NAMES_DOWNLOADED)}"
        )

        logger.debug(f"Job {self.ID} ran successfully.")


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    pass

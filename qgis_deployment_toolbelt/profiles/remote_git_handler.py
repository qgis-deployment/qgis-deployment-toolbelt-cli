#! python3  # noqa: E265

"""
Handle remote git repository.

Author: Julien Moura (https://github.com/guts).

Inspired from: QGIS Resource Sharing
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging

# project
from qgis_deployment_toolbelt.profiles.profiles_handler_base import (
    RemoteProfilesHandlerBase,
)


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################
class RemoteGitHandler(RemoteProfilesHandlerBase):
    """Handle remote git repository."""

    def __init__(
        self,
        source_repository_url: str,
        source_repository_type: str = "git_remote",
        branch_to_use: str | None = None,
    ) -> None:
        """Constructor.

        Args:
            source_repository_url (Union[str, Path]): input URI (http://, https://, git://)

        """
        super().__init__(
            source_repository_type=source_repository_type, branch_to_use=branch_to_use
        )

        self.SOURCE_REPOSITORY_PATH_OR_URL = source_repository_url

        # validation
        self.is_valid_git_repository()

        # check if passed branch exist
        if branch_to_use is None:
            self.DESTINATION_BRANCH_TO_USE = self.SOURCE_REPOSITORY_ACTIVE_BRANCH
            logger.info(
                "No branch specified. The default branch of source repository "
                f"({self.SOURCE_REPOSITORY_PATH_OR_URL}) will be used."
            )
        else:
            if not self.is_branch_existing_in_repository(branch_name=branch_to_use):
                logger.error(
                    f"Specified branch '{branch_to_use}' has not been found in source "
                    f"repository ({self.SOURCE_REPOSITORY_PATH_OR_URL}). Fallback to "
                    f"identified active branch: {self.SOURCE_REPOSITORY_ACTIVE_BRANCH}."
                )
                self.DESTINATION_BRANCH_TO_USE = self.SOURCE_REPOSITORY_ACTIVE_BRANCH
            else:
                self.DESTINATION_BRANCH_TO_USE = branch_to_use


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    pass

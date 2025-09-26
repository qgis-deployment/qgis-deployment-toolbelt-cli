#! python3  # noqa: E265

"""
Handle local git repository.

Author: Julien Moura (https://github.com/guts).

Inspired from: QGIS Resource Sharing
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from pathlib import Path

# project
from qgis_deployment_toolbelt.profiles.profiles_handler_base import (
    RemoteProfilesHandlerBase,
)
from qgis_deployment_toolbelt.utils.check_path import check_path, check_var_can_be_path


# 3rd party


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################
class LocalGitHandler(RemoteProfilesHandlerBase):
    """Handle local git repository."""

    def __init__(
        self,
        source_repository_path_or_uri: str | Path,
        source_repository_type: str = "git_local",
        branch_to_use: str | None = None,
    ) -> None:
        """Constructor.

        Args:
            source_repository_path_or_uri (str | Path): path to the source repository

        Raises:
            NotGitRepository: if uri_or_path doesn't point to a valid Git repository
        """
        super().__init__(
            source_repository_type=source_repository_type, branch_to_use=branch_to_use
        )

        # clean up
        if isinstance(
            source_repository_path_or_uri, str
        ) and source_repository_path_or_uri.startswith("file://"):
            source_repository_path_or_uri = source_repository_path_or_uri[7:]
            logger.debug(
                f"URI cleaning: 'file://' protocol prefix removed. Result: {source_repository_path_or_uri}"
            )
        if isinstance(
            source_repository_path_or_uri, str
        ) and source_repository_path_or_uri.endswith(".git"):
            logger.debug(
                f"URI cleaning: '.git' suffix removed. Result: {source_repository_path_or_uri}"
            )
            source_repository_path_or_uri = source_repository_path_or_uri[:-4]

        if isinstance(source_repository_path_or_uri, str) and check_var_can_be_path(
            input_var=source_repository_path_or_uri
        ):
            source_repository_path_or_uri = Path(
                source_repository_path_or_uri
            ).resolve()

        if isinstance(source_repository_path_or_uri, Path) and check_path(
            input_path=source_repository_path_or_uri,
            must_be_a_file=False,
            must_be_a_folder=True,
            must_exists=True,
            must_be_readable=True,
        ):
            source_repository_path_or_uri = source_repository_path_or_uri.resolve()

        self.SOURCE_REPOSITORY_PATH_OR_URL = source_repository_path_or_uri

        # validation
        self.is_valid_git_repository()

        self.SOURCE_REPOSITORY_ACTIVE_BRANCH = (
            self.get_active_branch_from_local_repository()
        )

        # check if passed branch exist
        if branch_to_use is None:
            self.DESTINATION_BRANCH_TO_USE = self.SOURCE_REPOSITORY_ACTIVE_BRANCH
            logger.info(
                "No branch specified. The active branch "
                f"({self.SOURCE_REPOSITORY_ACTIVE_BRANCH}) of source repository "
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

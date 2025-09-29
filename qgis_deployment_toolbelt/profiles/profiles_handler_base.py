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
from pathlib import Path
from shutil import rmtree
from typing import Literal

# 3rd party
from dulwich import porcelain
from dulwich.client import LsRemoteResult
from dulwich.errors import GitProtocolError, NotGitRepository
from dulwich.repo import Repo
from giturlparse import GitUrlParsed, parse as git_parse, validate as git_validate

# project
from qgis_deployment_toolbelt.utils import proxies
from qgis_deployment_toolbelt.utils.check_path import check_folder_is_empty


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################
class RemoteProfilesHandlerBase:
    """Common git repository handler using dulwich.

    It's designed to handle thoses cases:

    - the distant repository (source) is on a local network or drive
    - the distant repository (source) is on Internet (github.com, gitlab.com, gitlab.company.org...)
    - the local repository (destination) is on a local network or drive
    """

    SOURCE_REPOSITORY_ACTIVE_BRANCH: str | None = None
    SOURCE_REPOSITORY_PATH_OR_URL: Path | str | None = None
    SOURCE_REPOSITORY_TYPE: (
        Literal["git_local", "git_remote", "http", "local", "remote"] | None
    ) = None

    DESTINATION_PATH: Path | None = None
    DESTINATION_BRANCH_TO_USE: str | None = None

    def __init__(
        self,
        source_repository_type: Literal[
            "git_local", "git_remote", "http", "local", "remote"
        ],
        branch_to_use: str | None = None,
    ) -> None:
        """Object instanciation.

        Args:
            source_repository_type (Literal["git_local", "git_remote", "local", "remote"]): type of source
                repository
            branch_to_use (str | None, optional): branch to clone or checkout. If None,
                the source active branch will be used. Defaults to None.
        """
        self.DESTINATION_BRANCH_TO_USE = branch_to_use
        self.SOURCE_REPOSITORY_TYPE = source_repository_type

    def url_parsed(self, remote_git_url: str) -> GitUrlParsed:
        """Return URL parsed to extract git information.

        Returns:
            GitUrlParsed: parsed URL object
        """
        return git_parse(remote_git_url)

    def is_valid_git_repository(
        self,
        source_repository_path_or_url: Path | str | None = None,
        force_type: Literal["git_local", "git_remote", "local", "remote"] | None = None,
        raise_error: bool = True,
    ) -> bool:
        """Determine if the given path or URL is a valid repository or not.

        Args:
            source_repository_path_or_url (Path | str | None, optional): _description_.
                Defaults to None.
            force_type (Literal["git_local","local", "remote"], optional): force git repository
                type to check. If None, it uses the SOURCE_REPOSITORY_TYPE attribute.
                Defaults None.
            raise_error (bool, optional): if True, it raises an exception. Defaults
                to True.

        Raises:
            NotGitRepository: if given path or URL is not a valid Git repository

        Returns:
            bool: True if the given path or URL is a valid Git repository
        """
        valid_source = True

        # if no local git repository passed, try to use URL defined at object level
        if source_repository_path_or_url is None and isinstance(
            self.SOURCE_REPOSITORY_PATH_OR_URL, (Path, str)
        ):
            source_repository_path_or_url: str | Path = (
                self.SOURCE_REPOSITORY_PATH_OR_URL
            )
            logger.info(
                f"Using source repository set at object's level: {source_repository_path_or_url}"
            )

        # use the repository type if forced or attribute
        if force_type is None:
            repository_type = self.SOURCE_REPOSITORY_TYPE
        else:
            repository_type = force_type

        # check according to the repository types
        if repository_type in (
            "git_remote",
            "remote",
        ) and not self._is_url_git_repository(
            remote_git_url=source_repository_path_or_url,
            raise_error=False,
        ):
            valid_source = False
        elif repository_type in (
            "git_local",
            "local",
        ) and not self._is_local_path_git_repository(
            local_path=source_repository_path_or_url,
            raise_error=False,
        ):
            valid_source = False

        # log and/or raise
        err_message = f"{source_repository_path_or_url} is not a valid repository."
        if not valid_source and raise_error:
            raise NotGitRepository(
                f"{source_repository_path_or_url} is not a valid repository."
            )
        elif not valid_source:
            logger.debug(err_message)
        else:
            logger.debug(
                f"{source_repository_path_or_url} is a valid "
                f"{self.SOURCE_REPOSITORY_TYPE} repository."
            )

        return valid_source

    def _is_local_path_git_repository(
        self, local_path: Path | None = None, raise_error: bool = True
    ) -> bool:
        """Check if local folder is a git repository.

        Args:
            local_path (Path, optional): path to check
            raise_error (bool, optional): if enabled, log message is an error, debug
                if not. Defaults to True.

        Returns:
            bool: True if there is a .git subfolder
        """
        # if no local git repository passed, try to use URL defined at object level
        if local_path is None and isinstance(self.SOURCE_REPOSITORY_PATH_OR_URL, Path):
            local_path: Path = self.SOURCE_REPOSITORY_PATH_OR_URL

        try:
            porcelain.open_repo_closing(f"{local_path.resolve()}")
            return True
        except NotGitRepository as err:
            if not raise_error:
                logger.debug(f"{local_path} is not a valid Git repository")
                return False
            logger.error(f"{local_path} is not a valid Git repository. Trace: {err}")
            return False
        except Exception as err:
            logger.error(
                f"Something went wrong when checking if {local_path} is a valid "
                f"Git repository. Trace: {err}"
            )
            return False

    def _is_url_git_repository(
        self, remote_git_url: str | None = None, raise_error: bool = True
    ) -> bool:
        """Check if the remote URL is a git repository.

        Args:
            remote_git_url (str): URL pointing to a remote git repository.
            raise_error (bool, optional): if enabled, log message is an error, debug
                if not. Defaults to True.

        Returns:
            bool: True if the URL is a valid git repository.
        """
        # if remote git URL not passed, try to use URL defined at object level
        if remote_git_url is None and isinstance(
            self.SOURCE_REPOSITORY_PATH_OR_URL, str
        ):
            remote_git_url = self.SOURCE_REPOSITORY_PATH_OR_URL

        try:
            return git_validate(remote_git_url)
        except Exception as err:
            if not raise_error:
                logger.debug(f"{remote_git_url} is not a valid Git repository")
                return False
            logger.error(
                f"{remote_git_url} is not a valid Git repository. Trace: {err}"
            )
            return False

    @proxies.os_env_proxy
    def get_active_branch_from_local_repository(
        self, local_git_repository_path: Path | None = None
    ) -> str:
        """Retrieve git active branch from a local repository. Mainly a checker and a
            wrapper around dulwich logic.

        Args:
            local_git_repository_path (Path | None, optional): path to the local
                repository. If not defined, the SOURCE_REPOSITORY_PATH_OR_URL object's
                attribute is used if it exists. Defaults to None.

        Raises:
            NotGitRepository: if the path is not a valid Git Repository

        Returns:
            str: branch name
        """
        # if no local git repository passed, try to use URL defined at object level
        if local_git_repository_path is None and isinstance(
            self.SOURCE_REPOSITORY_PATH_OR_URL, Path
        ):
            local_git_repository_path: Path = self.SOURCE_REPOSITORY_PATH_OR_URL

        self.is_valid_git_repository(
            source_repository_path_or_url=local_git_repository_path
        )

        return porcelain.active_branch(
            repo=f"{local_git_repository_path.resolve()}"
        ).decode()

    def is_branch_existing_in_repository(
        self,
        branch_name: str | bytes,
        repository_path_or_url: Path | str | None = None,
    ) -> bool:
        """Determine if the given branch name is part of the given repository.

        Args:
            branch_name (str | bytes): _description_
            repository_path_or_url (Path | str, optional): URL or path pointing to a
                git repository. If None, it uses the SOURCE_REPOSITORY_PATH_OR_URL
                object's attribute

        Raises:
            NotGitRepository: if the path is not a valid Git Repository

        Returns:
            bool: True is the rbanch is part of given repository existing branches
        """
        # make sure this is string
        if isinstance(branch_name, bytes):
            branch_name = branch_name.decode()

        # if no local git repository passed, try to use URL defined at object level
        if repository_path_or_url is None and isinstance(
            self.SOURCE_REPOSITORY_PATH_OR_URL, (Path, str)
        ):
            repository_path_or_url: Path | str = self.SOURCE_REPOSITORY_PATH_OR_URL

        # check if URL or path is pointing to a valid git repository
        if not self.is_valid_git_repository(
            source_repository_path_or_url=repository_path_or_url
        ):
            raise NotGitRepository(
                f"{repository_path_or_url} is not a valid repository."
            )

        # clean branch name
        refs_heads_prefix = "refs/heads/"
        branch_name = branch_name.removeprefix(refs_heads_prefix)

        return branch_name in [
            branch.removeprefix(refs_heads_prefix)
            for branch in self.list_remote_branches(
                source_repository_path_or_url=repository_path_or_url
            )
        ]

    @proxies.os_env_proxy
    def list_remote_branches(
        self, source_repository_path_or_url: Path | str | None = None
    ) -> tuple[str]:
        """Retrieve git active branch from a local repository. Mainly a checker and a
            wrapper around dulwich logic.

        Args:
            source_repository_path_or_url (Path | str, optional): URL or path pointing
                to a git repository.

        Raises:
            NotGitRepository: if the path is not a valid Git Repository

        Returns:
            tuple[str]: tuple of branch complete names \
                ('refs/heads/profile-for-qgis-3-34', 'refs/heads/main')
        """
        # if no local git repository passed, try to use URL defined at object level
        if source_repository_path_or_url is None and isinstance(
            self.SOURCE_REPOSITORY_PATH_OR_URL, (Path, str)
        ):
            source_repository_path_or_url: Path | str = (
                self.SOURCE_REPOSITORY_PATH_OR_URL
            )

        # check if URL or path is pointing to a valid git repository
        if not self.is_valid_git_repository(
            source_repository_path_or_url=source_repository_path_or_url
        ):
            raise NotGitRepository(
                f"{source_repository_path_or_url} is not a valid repository."
            )

        ls_remote_refs: LsRemoteResult | dict = porcelain.ls_remote(
            remote=f"{source_repository_path_or_url}"
        )

        source_repository_branches = []

        if isinstance(ls_remote_refs, LsRemoteResult) and len(ls_remote_refs.refs) > 0:
            source_repository_branches = [
                ref.decode()
                for ref in ls_remote_refs.refs
                if ref.startswith(b"refs/heads/")
            ]
        elif isinstance(ls_remote_refs, dict) and len(ls_remote_refs) > 0:
            source_repository_branches = [
                ref.decode() for ref in ls_remote_refs if ref.startswith(b"refs/heads/")
            ]

        if source_repository_branches:
            logger.debug(
                f"{len(source_repository_branches)} branche(s) found in repository "
                f"{source_repository_path_or_url}: "
                f"{' ; '.join(source_repository_branches)}"
            )
            return tuple(source_repository_branches)
        else:
            logger.debug(
                f"No branch found in repository {source_repository_path_or_url}"
            )
            return ("",)

    @proxies.os_env_proxy
    def download(self, destination_local_path: Path) -> Repo:
        """Generic wrapper around the specific logic of this handler.

        Args:
            destination_local_path (Path): path to the local folder where to download

        Returns:
            Repo: the local repository object
        """
        if isinstance(destination_local_path, Path):
            destination_local_path = destination_local_path.resolve()

        local_git_repository = self.clone_or_pull(
            to_local_destination_path=destination_local_path
        )

        if isinstance(local_git_repository, Repo):
            self.DESTINATION_BRANCH_TO_USE = porcelain.active_branch(
                local_git_repository
            ).decode()

        return local_git_repository

    def clone_or_pull(self, to_local_destination_path: Path, attempt: int = 1) -> Repo:
        """Clone or fetch/pull remote repository to local path. If this one doesn't exist,
        it's created. If fetch or pull action fail, it removes the existing folder and
        clone the remote again.

        Args:
            to_local_destination_path (Path): path to the folder where to clone (or pull)
            attempt (int): attempt count. If attempts < 2 and it fails, the destination
                path is completely removed before cloning again. Defaults to 1.

        Raises:
            err: if something fails during clone or pull operations

        Returns:
            Repo: the local repository object
        """
        # clone
        if (
            not to_local_destination_path.exists()
            or check_folder_is_empty(to_local_destination_path)
        ) and not self.is_valid_git_repository(
            source_repository_path_or_url=to_local_destination_path,
            raise_error=False,
            force_type="git_local",
        ):
            try:
                logger.debug("Start cloning operations...")
                return self._clone(local_path=to_local_destination_path)
            except Exception as err:
                logger.error(
                    "Error cloning the source repository "
                    f"{self.SOURCE_REPOSITORY_PATH_OR_URL} "
                    f"(branch {self.SOURCE_REPOSITORY_ACTIVE_BRANCH}) "
                    f"to {to_local_destination_path}. "
                    f"Trace: {err}."
                )
                if attempt < 2:
                    logger.error(
                        "Clone fail 1/2. Removing target folder and trying again..."
                    )
                    rmtree(path=to_local_destination_path, ignore_errors=True)
                    return self.clone_or_pull(
                        to_local_destination_path=to_local_destination_path, attempt=2
                    )
                logger.critical("Clone fail 2/2. Abort.")
                rmtree(path=to_local_destination_path, ignore_errors=True)
                raise err
        elif to_local_destination_path.exists() and self.is_valid_git_repository(
            source_repository_path_or_url=to_local_destination_path,
            raise_error=False,
            force_type="git_local",
        ):
            # FETCH
            logger.debug("Start fetching operations...")
            try:
                self._fetch(local_path=to_local_destination_path)
            except GitProtocolError as error:
                logger.error(
                    "Error fetching source repository "
                    f"{self.SOURCE_REPOSITORY_PATH_OR_URL} "
                    f"to {to_local_destination_path.resolve()}. Trace: {error}."
                )
                rmtree(path=to_local_destination_path, ignore_errors=True)
                return self.clone_or_pull(
                    to_local_destination_path=to_local_destination_path
                )
            # PULL
            logger.debug("Start pulling operations...")
            try:
                return self._pull(local_path=to_local_destination_path)
            except GitProtocolError as error:
                logger.error(
                    f"Error pulling {self.SOURCE_REPOSITORY_PATH_OR_URL} "
                    f"repository to {to_local_destination_path.resolve()}. Trace: {error}."
                    "Trying to remove the local folder and cloning again..."
                )
                rmtree(path=to_local_destination_path, ignore_errors=True)
                return self.clone_or_pull(
                    to_local_destination_path=to_local_destination_path
                )
        elif not to_local_destination_path.exists():
            logger.debug(
                f"Local path does not exists: {to_local_destination_path.as_uri()}. "
                "Creating it and trying again..."
            )
            to_local_destination_path.mkdir(parents=True, exist_ok=True)
            return self.clone_or_pull(
                to_local_destination_path=to_local_destination_path
            )
        else:
            logger.critical(
                f"Case not handle. Context: {to_local_destination_path} "
                f"(empty={check_folder_is_empty(to_local_destination_path)}) "
                f"valid repo={self.is_valid_git_repository(source_repository_path_or_url=to_local_destination_path, raise_error=False)}"
            )
            return None

    @proxies.os_env_proxy
    def _clone(self, local_path: Path) -> Repo:
        """Clone the remote repository to local path.

        Args:
            local_path (Path): path to the folder where to clone

        Returns:
            Repo: the local repository object
        """
        # make sure folder and its parents exist
        if not local_path.exists():
            local_path.mkdir(parents=True, exist_ok=True)

        # make sure branch is bytes
        if isinstance(self.DESTINATION_BRANCH_TO_USE, str) and len(
            self.DESTINATION_BRANCH_TO_USE
        ):
            branch = self.DESTINATION_BRANCH_TO_USE.encode()
        elif isinstance(self.DESTINATION_BRANCH_TO_USE, bytes):
            branch = self.DESTINATION_BRANCH_TO_USE
        else:
            branch = None

        logger.debug(
            f"Cloning repository {self.SOURCE_REPOSITORY_PATH_OR_URL} ({branch=}) to {local_path}"
        )

        if self.SOURCE_REPOSITORY_TYPE in ("git_local", "local"):
            with porcelain.open_repo_closing(
                path_or_repo=self.SOURCE_REPOSITORY_PATH_OR_URL.as_posix()
            ) as src_repo_obj:
                repo_obj = src_repo_obj.clone(
                    target_path=f"{local_path.resolve()}",
                    branch=branch,
                    mkdir=False,
                    checkout=True,
                    progress=None,
                )
        elif self.SOURCE_REPOSITORY_TYPE in ("git_remote", "remote"):
            repo_obj = porcelain.clone(
                source=self.SOURCE_REPOSITORY_PATH_OR_URL,
                target=f"{local_path.resolve()}",
                branch=branch,
            )
        else:
            raise NotImplementedError(f"{self.SOURCE_REPOSITORY_TYPE} is not supported")

        gobj = repo_obj.get_object(repo_obj.head())
        logger.debug(
            f"Active branch: {porcelain.active_branch(repo_obj)}. "
            f"Latest commit cloned: {gobj.sha().hexdigest()} by {gobj.author}"
            f" at {gobj.commit_time}."
        )
        repo_obj.close()
        return repo_obj

    @proxies.os_env_proxy
    def _fetch(self, local_path: Path) -> Repo:
        """Fetch the remote repository from the existing local repository.

        Args:
            local_path (Path): path to the folder where to fetch

        Returns:
            Repo: the local repository object
        """
        # if source repository is a local path, let's convert it into str
        if isinstance(self.SOURCE_REPOSITORY_PATH_OR_URL, Path):
            source_repository = f"{self.SOURCE_REPOSITORY_PATH_OR_URL.resolve()}"
        else:
            source_repository = str(self.SOURCE_REPOSITORY_PATH_OR_URL)

        # with porcelain.open_repo_closing(str(local_path.resolve())) as local_repo:
        logger.info(
            f"Fetching repository {source_repository} to {local_path}",
        )

        destination_local_repository = Repo(root=f"{local_path.resolve()}")
        porcelain.fetch(
            repo=destination_local_repository,
            remote_location=source_repository,
            force=True,
            prune=True,
            prune_tags=True,
        )
        destination_local_repository.close()

        logger.debug(
            f"Repository {local_path.resolve()} has been fetched from "
            f"remote {source_repository}. "
            f"Local active branch: {porcelain.active_branch(destination_local_repository)}."
        )

        return destination_local_repository

    @proxies.os_env_proxy
    def _pull(self, local_path: Path) -> Repo:
        """Pull the remote repository from the existing local repository.

        Args:
            local_path (Path): path to the folder where to pull

        Returns:
            Repo: the local repository object
        """
        # if source repository is a local path, let's convert it into str
        if isinstance(self.SOURCE_REPOSITORY_PATH_OR_URL, Path):
            source_repository = f"{self.SOURCE_REPOSITORY_PATH_OR_URL.resolve()}"
        else:
            source_repository = str(self.SOURCE_REPOSITORY_PATH_OR_URL)

        logger.info(f"Pulling repository {source_repository} to {local_path}")

        destination_local_repository = Repo(root=f"{local_path.resolve()}")
        porcelain.pull(
            repo=local_path,
            remote_location=source_repository,
            force=True,
        )
        gobj = destination_local_repository.get_object(
            destination_local_repository.head()
        )
        logger.debug(
            f"Repository {local_path.resolve()} has been pulled. "
            f"Local active branch: {porcelain.active_branch(destination_local_repository)}. "
            f"Latest commit cloned: {gobj.sha().hexdigest()} by {gobj.author}"
            f" at {gobj.commit_time}"
        )

        destination_local_repository.close()
        return destination_local_repository


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    pass

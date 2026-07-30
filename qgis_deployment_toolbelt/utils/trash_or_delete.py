#! python3  # noqa: E265

"""Util dedicated to manage removal of files and folders on disk using a configurable
deletion policy: moving them to the system trash, falling back to permanent deletion
when trashing fails, or skipping the trash entirely.

Author: Julien Moura (https://github.com/guts)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from os import getenv
from pathlib import Path
from shutil import rmtree
from typing import get_args

# 3rd party library
from send2trash import send2trash

# project
from qgis_deployment_toolbelt.constants import DEFAULT_DELETION_POLICY, DeletionPolicy


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Functions #############
# ##################################


def get_deletion_policy() -> DeletionPolicy:
    """Resolve the deletion policy from the ``QDT_DELETION_POLICY`` environment
    variable, falling back to the default when unset or invalid.

    Returns:
        DELETION_POLICY: resolved deletion policy.
    """
    deletion_policy_from_env = (
        getenv("QDT_DELETION_POLICY", DEFAULT_DELETION_POLICY).strip().lower()
    )
    if deletion_policy_from_env not in get_args(DeletionPolicy):
        logger.warning(
            "Invalid value for 'QDT_DELETION_POLICY' environment variable: "
            f"'{deletion_policy_from_env}'. "
            f"Valid values are: {', '.join(get_args(DeletionPolicy))}. "
            f"Falling back to the default: '{DEFAULT_DELETION_POLICY}'."
        )
        deletion_policy_from_env = DEFAULT_DELETION_POLICY

    return deletion_policy_from_env


def _permanently_delete(path: Path) -> None:
    """Permanently delete a file or folder.

    Args:
        path (Path): path to remove.

    Raises:
        OSError: if the removal fails.
    """
    if path.is_dir() and not path.is_symlink():
        rmtree(path=path)
    else:
        path.unlink(missing_ok=True)


def move_files_to_trash_or_delete(
    files_to_trash: list[Path] | Path,
    delete_file_per_file: bool = False,
    policy: DeletionPolicy | None = None,
) -> list[Path]:
    """Remove files or folders from disk, according to a deletion policy.

    Args:
        files_to_trash (list[Path] | Path): file/folder path or list of paths
            to remove.
        delete_file_per_file (bool, optional): only relevant for the
            "trash_only" and "trash_or_delete" policies. If False, it tries a
            single batch trash operation; if True, it works path per path.
            Defaults to False.
        policy (DELETION_POLICY | None, optional): deletion policy to apply.
            If None, it's resolved from the ``QDT_DELETION_POLICY``
            environment variable. Defaults to None.

    Returns:
        list[Path]: list of paths that failed to be removed (empty if all succeeded).
    """
    li_failed_to_remove: list[Path] = []

    # make sure it's a list
    if isinstance(files_to_trash, Path):
        files_to_trash = [
            files_to_trash,
        ]

    if not len(files_to_trash):
        logger.debug("Nothing to remove: empty list of paths.")
        return li_failed_to_remove

    # resolve policy with priority to the explicit argument over env var
    if policy is None:
        policy = get_deletion_policy()

    logger.debug(f"Removing {len(files_to_trash)} path(s) using '{policy}' policy.")

    # -- force_delete: bypass the trash entirely --
    if policy == "force_delete":
        for path in files_to_trash:
            try:
                _permanently_delete(path)
                logger.debug(f"{path} has been permanently deleted (force_delete).")
            except OSError as err:
                li_failed_to_remove.append(path)
                logger.exception(f"Unable to permanently delete {path}. Trace: {err}")
        return li_failed_to_remove

    # -- trash_only / trash_or_delete: first try a batch trash operation
    if not delete_file_per_file:
        try:
            send2trash(paths=files_to_trash)
            logger.debug(
                f"{len(files_to_trash)} files have been moved to the trash: {','.join(str(p) for p in files_to_trash)}"
            )
        except OSError as err:
            logger.exception(
                f"Moving {len(files_to_trash)} files to the trash in a single batch "
                f"operation failed. Let's try it file per file. Trace: {err}"
            )
            move_files_to_trash_or_delete(
                files_to_trash=files_to_trash,
                delete_file_per_file=True,
                policy=policy,
            )
    else:
        logger.debug(
            f"Moving (or deleting) {len(files_to_trash)} files to trash, using a file "
            f"per file operation (policy: '{policy}')."
        )
        for file_to_trash in files_to_trash:
            try:
                send2trash(paths=file_to_trash)
                logger.debug(f"{file_to_trash} has been moved to the trash.")
            except OSError as err:
                if policy == "trash_only":
                    logger.warning(
                        f"Unable to move {file_to_trash} to the trash and policy is "
                        f"'{policy}'. It's left untouched. Trace: {err}"
                    )
                    li_failed_to_remove.append(file_to_trash)
                    continue
                logger.warning(
                    f"Unable to move {file_to_trash} to the trash. Trace: {err}. "
                    f"Let's try to delete it directly (policy: '{policy}')."
                )
                try:
                    _permanently_delete(file_to_trash)
                    logger.debug(f"Deleting directly {file_to_trash} succeeded.")
                except OSError as err_delete:
                    logger.exception(
                        f"An error occurred trying to delete {file_to_trash}. "
                        f"Trace: {err_delete}"
                    )
                    li_failed_to_remove.append(file_to_trash)

    return li_failed_to_remove

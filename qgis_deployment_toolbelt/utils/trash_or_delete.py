#! python3  # noqa: E265

"""
    QDT autocleaner.

    Author: Julien Moura (https://github.com/guts)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from pathlib import Path

# 3rd party library
from send2trash import TrashPermissionError, send2trash

# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Functions #############
# ##################################


def move_files_to_trash_or_delete(
    files_to_trash: list[Path] | Path,
    attempt: int = 1,
) -> None:
    """Move files to the trash or directly delete them if it's not possible.

    Args:
        files_to_trash (list[Path] | Path): list of file paths to move to the trash
        attempt (int, optional): attempt (int): attempt count. If attempt < 2, it
            tries a single batch operation. If attempt == 2, it works file per file.
            Defaults to 1.
    """
    # make sure it's a list
    if isinstance(files_to_trash, Path):
        files_to_trash = [
            files_to_trash,
        ]

    # first try a batch
    if attempt < 2:
        try:
            send2trash(paths=files_to_trash)
            logger.info(f"{len(files_to_trash)} files have been moved to the trash.")
        except Exception as err:
            logger.error(
                f"Moving {len(files_to_trash)} files to the trash in a single batch "
                f"operation failed. Let's try it file per file. Trace: {err}"
            )
            move_files_to_trash_or_delete(files_to_trash=files_to_trash, attempt=2)
    else:
        logger.debug(
            f"Moving (or deleting) {len(files_to_trash)} files to trash: " "attempt 2"
        )
        for file_to_trash in files_to_trash:
            try:
                send2trash(paths=file_to_trash)
                logger.info(f"{file_to_trash} has been moved to the trash.")
            except TrashPermissionError as err:
                logger.warning(
                    f"Unable to move {file_to_trash} to the trash. "
                    f"Trace: {err}. Let's try to delete it directly."
                )
                try:
                    file_to_trash.unlink(missing_ok=True)
                    logger.info(f"Deleting directly {file_to_trash} succeeded.")
                except Exception as err:
                    logger.error(
                        f"An error occurred trying to delete {file_to_trash}. "
                        f"Trace: {err}"
                    )
            except Exception as err:
                logger.error(
                    f"An error occurred trying to move {file_to_trash} to trash. "
                    f"Trace: {err}"
                )

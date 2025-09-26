#! python3  # noqa: E265

"""Reader for qdt-files.json generated with tree."""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from typing import TypedDict


# #############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# #############################################################################
# ########## Classes ###############
# ##################################


class Treeitem(TypedDict):
    type: str
    name: str
    contents: list[dict] | None


# #############################################################################
# ########## Functions #############
# ##################################


def tree_to_download_list(tree_array: list[Treeitem], rel_path: str = "") -> list:
    """Parse tree structure and return a list of files to download with relative
        paths to the base URL. It's meant to be used as recursive funciton to iter
        through the tree structure.

    Args:
        tree_array (list[TreeItem]): input array from tree JSON structure.
        rel_path (str, optional): relative path to resolve from. Defaults to "".

    Returns:
        list: list of files paths relative to the base URL.
    """
    li_files = []

    if not isinstance(tree_array, (list, tuple)):
        return li_files

    for item in tree_array:
        if item.get("type") == "directory":
            if item.get("name") != ".":
                new_rel_path = f"{rel_path}/{item.get('name')}"
            else:
                new_rel_path = f"{item.get('name')}"

        if "contents" in item:
            li_files.extend(
                tree_to_download_list(
                    tree_array=item.get("contents"),
                    rel_path=new_rel_path,
                )
            )
        elif item.get("type") == "file":
            li_files.append(f"{rel_path}/{item.get('name')}")
        else:
            logger.debug(f"Unsupported item type: {item.get('type')}")

    return li_files

#! python3  # noqa: E265

"""
Utilities specific for Linux.

Author: Julien Moura (https://github.com/guts)

"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Literal

# project
from qgis_deployment_toolbelt.utils.check_path import check_path


# #############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)


# bash startup files
bash_system_dot_bash_profile: Path = Path("/etc/profile.d/qdt")
bash_user_dot_bash_profile: Path = Path.home().joinpath(".bash_profile")
bash_user_dot_bash_login: Path = Path.home().joinpath(".bash_login")
bash_user_dot_profile: Path = Path.home().joinpath(".profile")

# QDT block in-file
qdt_block_comment_start = "# BEGIN QDT MANAGED BLOCK"
qdt_block_comment_end = "# END QDT MANAGED BLOCK"


shell_path_to_names = {
    "bash": ("/bin/bash", "/usr/bin/bash"),
}

# #############################################################################
# ########## Functions #############
# ##################################


def bash_user_which_file_to_store() -> Path:
    """Determine which file to use to store environment variables.

    Returns:
        Path: path to the file to use
    """
    # check if one of the bash file exists and using it. Order matters.
    if bash_user_dot_bash_profile.is_file():
        logger.debug(
            f"Using {bash_user_dot_bash_profile} to store environment variables."
        )
        return bash_user_dot_bash_profile
    elif bash_user_dot_bash_login.is_file():
        logger.debug(
            f"Using {bash_user_dot_bash_login} to store environment variables."
        )
        return bash_user_dot_bash_login
    elif bash_user_dot_profile.is_file():
        logger.debug(f"Using {bash_user_dot_profile} to store environment variables.")
        return bash_user_dot_profile

    logger.info(
        f"None of the files exist. Creating and using {bash_user_dot_profile} to store "
        "environment variables."
    )
    bash_user_dot_profile.touch()
    return bash_user_dot_profile


@lru_cache
def find_key_from_values(value_to_find: str) -> str | None:
    """Finds the key corresponding to a given value in a dictionary where values are
    tuples.

    Args:
        value_to_find (str): The value to search for in the dictionary values.

    Returns:
        str | None: The key corresponding to the found value. Returns None if the value
            is not found.
    """

    for key, values in shell_path_to_names.items():
        if value_to_find in values:
            return key
    return None


def get_environment_variable(envvar_name: str, scope: str = "user") -> str | None:
    """Get environment variable from Linux profile file
    Args:
        envvar_name (str): environment variable name (= key) to retrieve
        scope (str, optional): environment variable scope. Must be "user" or "system",
            defaults to "user". Defaults to "user".

    Returns:
        str | None: environment variable value or None if not found
    """

    profile_file = get_profile_file(scope)

    if profile_file is not None:
        logger.debug(f"parsing {profile_file}")

        # Read file content
        with profile_file.open(mode="r", encoding="UTF-8") as file:
            lines = file.readlines()

        # look for export line
        env_value = None
        for line in lines:
            if envvar_name in line.strip():
                env_value = [item.strip() for item in re.split("=", line)][-1]

        logger.debug(f"Value for environment variable {envvar_name}: {env_value}")

        return env_value
    else:
        logger.error("Profile file was not found.")
        return None


def set_environment_variable(
    envvar_name: str, envvar_value: str | bool | int, scope: str = "user"
) -> bool:
    """Set environment variable in Linux profile file
    Args:
        envvar_name (str): environment variable name (= key) to set
        envvar_value (str): environment variable value to set
        scope (str, optional): environment variable scope. Must be "user" or "system",
            defaults to "user". Defaults to "user".

    Returns:
        bool: True if environment variable correctly set or False if not
    """

    if isinstance(envvar_value, bool):
        envvar_value = str(bool(envvar_value)).lower()

    if get_environment_variable(envvar_name, scope) is not None:
        logger.info(f"Environment variable {envvar_name} already there")
        if get_environment_variable(envvar_name, scope) != envvar_value:
            logger.info("Environment variable value to be changed")
            delete_environment_variable(envvar_name)
        else:
            logger.info(f"Environment variable already set to {envvar_value}")
            return True

    profile_file = get_profile_file(scope)

    if profile_file is not None:
        logger.debug(f"parsing {profile_file}")

        export_line = f"export {envvar_name}={str(envvar_value)}"
        block_start_found = False
        block_end_found = False
        block_end_line: int = 0
        line_found = False

        # Read file content
        with profile_file.open(mode="r", encoding="UTF-8") as file:
            lines = file.readlines()

        # look for block and export line
        line_number: int = 0
        for line in lines:
            if line.strip() == qdt_block_comment_start:
                block_start_found = True
            elif line.strip() == qdt_block_comment_end:
                block_end_found = True
                block_end_line = line_number
            elif line.strip() == export_line:
                line_found = True
            # line counter
            line_number += 1

        # check if block exist
        block_found = all([block_start_found, block_end_found])

        if line_found:
            logger.debug(
                f"Environment variable and key {envvar_name}={envvar_value} is already present"
            )
            return True
        else:
            if block_found:
                lines.insert(block_end_line, f"{export_line}\n")

                with profile_file.open(mode="w", encoding="UTF-8") as file:
                    file.writelines(lines)
                logger.info(
                    f"QDT block was already here but not the line: '{export_line}. "
                    "It has been added."
                )
                return True
            else:
                new_lines = (
                    f"\n{qdt_block_comment_start}\n",
                    f"{export_line}\n",
                    f"{qdt_block_comment_end}",
                )
                with profile_file.open(mode="a", encoding="UTF-8") as file:
                    file.writelines(new_lines)
                logger.info(
                    f"Nor QDT block and the line: '{export_line}' were present. "
                    "Both have been added."
                )
                return True
    else:
        logger.error("Profile file was not found.")
        return False


def delete_environment_variable(
    envvar_name: str, scope: Literal["system", "user"] = "user"
) -> bool:
    """Remove environment variable from Linux profile file
    Args:
        envvar_name (str): environment variable name (= key) to remove
        scope (str, optional): environment variable scope. Must be "user" or "system",
            defaults to "user". Defaults to "user".

    Returns:
        bool: True if environment variable successfully removed or False if not
    """
    # check and get profile file
    profile_file = get_profile_file(scope=scope)
    if not profile_file:
        logger.error("Profile file was not found.")
        return False

    # start parsing it
    logger.debug(f"Parsing {profile_file}")

    line_begin = f"export {envvar_name}="
    block_start_found = False
    block_start_line: int = 0
    block_end_found = False
    block_end_line: int = 0
    line_found = False
    line_begin_line: int = 0

    # read file content
    with profile_file.open(mode="r", encoding="UTF-8") as file:
        lines = file.readlines()

    # look for block and beginning of line
    line_number: int = 0
    for line in lines:
        if line.strip() == qdt_block_comment_start:
            block_start_found = True
            block_start_line = line_number
        elif line.strip() == qdt_block_comment_end:
            block_end_found = True
            block_end_line = line_number
        elif line_begin in line.strip():
            line_found = True
            line_begin_line = line_number
        # line counter
        line_number += 1

    # check if block exist
    all([block_start_found, block_end_found])

    pos = []
    if line_found:
        pos.append(line_begin_line)
        logger.debug(
            f"Environment variable and key {envvar_name} was found. It will be removed"
        )
    if block_start_found:
        pos.append(block_start_line)
        logger.debug(
            f"QDT block start was found for '{envvar_name}'. Block start will be removed."
        )
    if block_end_found:
        pos.append(block_end_line)
        logger.info(
            f"QDT block end was found for: '{envvar_name}'. Block end will be removed."
        )

    new_lines = [lines[i] for i, e in enumerate(lines) if i not in pos]
    with profile_file.open(mode="w", encoding="UTF-8") as file:
        file.writelines(new_lines)
    logger.info(
        f"QDT block for environment variable '{envvar_name}' has been removed. "
        "Shell profile updated."
    )
    return True


def refresh_environment() -> bool:
    """Just here to be equivalent with Windows logic.

    TODO: refacto merging win32 methods in a single class.

    Returns:
        bool: always True
    """
    logger.info(
        "Changes in environment variables wont' be applied until you log out/log in or "
        f"reload your profile: 'bash source {bash_user_which_file_to_store()}'"
    )
    return True


def get_profile_file(scope: Literal["system", "user"]) -> Path | None:
    """Get Linux profile file depending on shell and scope
    Args:
        scope (str, optional): environment variable scope. Must be "user" or "system",
            defaults to "user". Defaults to "user".

    Returns:
        str | None: profile file path or None if not found
    """
    if scope == "system":
        try:
            if not bash_system_dot_bash_profile.is_file():
                bash_system_dot_bash_profile.touch()
            check_path(
                input_path=bash_system_dot_bash_profile,
                must_be_a_file=True,
                must_exists=True,
                must_be_writable=True,
                must_be_readable=True,
            )
            logger.debug(
                f"{bash_system_dot_bash_profile} exists and it's writable. It will be used."
            )
            return bash_system_dot_bash_profile
        except PermissionError as err:
            logger.error(
                f"{bash_system_dot_bash_profile} is not accessible to the user. Trace: {err}"
            )
            return

    elif scope == "user":
        return bash_user_which_file_to_store()
    else:
        logger.error(f"Scope {scope} not handled. Fallback to 'user'.")
        return get_profile_file(scope="user")

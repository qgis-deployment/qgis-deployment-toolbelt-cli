#! python3  # noqa: E265

"""
Utilities to manage user security groups either on Linux and Windows.

Author: Julien Moura (https://github.com/guts)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import logging
import subprocess
from functools import lru_cache
from getpass import getuser
from platform import uname
from sys import platform as opersys


# Imports depending on operating system
if opersys == "win32":
    """windows"""
    # standard
    import shutil

    # 3rd party
    import pyad
    import win32com
    import win32net
    from pywintypes import error as PyWinException  # noqa: N812

else:
    import grp

# package
from qgis_deployment_toolbelt.utils.win32utils import (
    ExtendedNameFormat,
    get_current_user_extended_data,
)


# #############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)


# #############################################################################
# ########## Functions #############
# ##################################


@lru_cache
def get_user_active_directory_object() -> "pyad.ADUser | None":
    """Get user as an Active Directory object.

    Returns:
        pyad.ADUser | None: user object or None if something went wrong
    """
    user_obj = None
    user_guid_or_name = get_user_name_or_guid()
    try:
        if user_guid_or_name.startswith("{"):
            user_obj = pyad.aduser.ADUser.from_guid(user_guid_or_name)
        else:
            user_obj = pyad.aduser.ADUser.from_cn(user_guid_or_name)
    except Exception as err:
        logger.error(f"Unable to get the user object. Trace: {err}")
    return user_obj


@lru_cache
def get_user_name_or_guid() -> str:
    """Get user GUID or name as fallback.

    Returns:
        str: user GUID or name (getpass.getuser())
    """
    if opersys.lower() in ("win32", "windows"):
        try:
            user_guid_or_name = get_current_user_extended_data(
                ExtendedNameFormat.NameUniqueId
            )
            logger.debug(
                f"Using user GUID to retrieve domain groups: {user_guid_or_name}"
            )
        except Exception as err:
            logger.info(
                f"Unable to retrieve user GUID. Fallback to user name. Trace: {err}"
            )
    else:
        user_guid_or_name = getuser()
        logger.debug(f"Using username to retrieve domain groups: {user_guid_or_name}")

    return user_guid_or_name


@lru_cache
def get_user_local_groups(user_name: str | None = None) -> list[str]:
    """Lists the local groups to which the user belong.

    On Linux and MacOS, it relies on the grp module (only available).
    On Windows, it relies on win32net (COM).

    Args:
        user_name (str | None, optional): name of user. If None, the current user name
            is used. Defaults to None.

    Raises:
        NotImplementedError: if operating system is not supported.

    Returns:
        list[str]: sorted list of unique groups names
    """
    if user_name is None:
        user_name = getuser()

    if opersys.lower() in ("darwin", "linux"):
        return sorted({g.gr_name for g in grp.getgrall() if user_name in g.gr_mem})
    elif opersys.lower() in ("win32", "windows"):
        server_host_name = uname()[1]
        try:
            local_groups = sorted(
                set(win32net.NetUserGetLocalGroups(server_host_name, user_name))
            )
        except PyWinException as err:
            logger.info(
                f"Retrieving user ('{user_name}') local groups on {server_host_name} "
                "failed. This usually means that it's not a local session, and that the "
                "computer is linked to a domain and subscribed to a directory. "
                f"Trace: {err}"
            )
            local_groups = []
        return local_groups
    else:
        raise NotImplementedError(f"Unsupported operating system: {opersys}")


@lru_cache
def get_user_domain_groups(user_guid_or_name: str | None = None) -> list[str]:
    """Lists the domain groups to which the user belong.

    On Linux and MacOS, it always return an empty list. TODO: implement it (probably
        using pure LDAP).
    On Windows, it relies on win32net (COM).

    Args:
        user_guid_or_name (str | None, optional): name of user. If None, the current user name
            is used. Defaults to None.

    Raises:
        NotImplementedError: if operating system is not supported.

    Returns:
        list[str]: sorted list of unique groups names
    """
    if user_guid_or_name is None:
        user_guid_or_name = get_user_name_or_guid()

    if not is_computer_attached_to_a_domain():
        logger.debug(
            "Computer is not attached to a domain so retrieving user's domain groups "
            "is meaningless. Returning empty list."
        )
        return []

    if opersys.lower() in ("darwin", "linux"):
        # TODO: find a way to retrive user's domain groups on Linux and MacOS (probably
        #  using pure ldap)
        return []
    elif opersys.lower() in ("win32", "windows"):
        user_obj = get_user_active_directory_object()
        user_groups: list[pyad.ADGroup] | None = user_obj.get_memberOfs()
        if not user_groups or not len(user_groups):
            logger.warning(
                f"It looks like '{user_guid_or_name}' does not belong to any domain group."
            )
            return []
        else:
            logger.info(
                f"The current user '{user_guid_or_name}' belongs to {len(user_groups)} Active "
                "Directory groups."
            )

        return sorted(
            {
                grp.get_attribute("name")[0]
                for grp in user_groups
                if isinstance(grp, pyad.ADGroup)
            }
        )
    else:
        raise NotImplementedError(f"Unsupported operating system: {opersys}")


def _is_computer_in_domain_powershell() -> bool:
    """Check if the computer is joined to a domain or a workgroup using PowerShell.

    Returns:
        bool: True if the computer is joined to a domain or workgroup, False otherwise.
    """
    powershell_path = shutil.which("powershell.exe")
    if not powershell_path:
        raise FileNotFoundError("powershell.exe not found in PATH.")

    # use PowerShell to retrieve domain information
    domain = subprocess.run(  # noqa: S603
        [powershell_path, "-Command", "(Get-CimInstance Win32_ComputerSystem).Domain"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    ).stdout.strip()

    # check if domain is different from workgroup
    return domain.lower() != "workgroup"


def _is_computer_in_domain_pyad() -> bool:
    """Check if the computer is joined to a domain or a workgroup using PyAD.

    Returns:
        bool: True if the computer is joined to a domain or workgroup, False otherwise.
    """
    try:
        user_obj = get_user_active_directory_object()
        return bool(len(user_obj.get_attribute("memberOf")))
    except Exception as err:
        logger.info(
            f"Based on pyad, the current computer is not attached to any domain. Trace: {err}"
        )
        return False


def _is_computer_in_domain_win32() -> bool:
    """Check if the computer is joined to a domain or a workgroup using win32com.

    Returns:
        bool: True if the computer is joined to a domain or workgroup, False otherwise.
    """
    # try to import wmi
    try:
        wmi = win32com.client.GetObject("winmgmts://./root/cimv2")
    except Exception as err:
        logger.info(
            "Unable to load WMI (Windows Management Instrumentation) from "
            f"win32com.client. Other options will be used. Trace: {err}"
        )
        raise err

    try:
        # Execute a query to retrieve information about the domain
        query = "SELECT * FROM Win32_ComputerSystem"
        result = wmi.ExecQuery(query)

        # Check if the domain attribute is not None
        for item in result:
            if item.Domain and item.Domain.lower() != "workgroup":
                logger.debug(f"Computer is joined to a domain: {item.Domain.lower()}")
                return True

    except Exception as err:
        logger.error(f"Getting domain from WMI through win32com failed. Trace: {err}")
        raise err

    return False


@lru_cache
def is_computer_attached_to_a_domain() -> bool:
    """Determine if the computer is attached to a domain or not.

    On Linux and MacOS, it always return False.
    On Windows, it tries to use wmi (Windows Management Instrumentation), Active
        Directory (through pyad) or subprocessed powershell as final fallback.

    Raises:
        NotImplementedError: if operating system is not supported.

    Returns:
        bool: True if the computer is attached to a domain.
    """
    if opersys.lower() in ("darwin", "linux"):
        # TODO: find a way to determine if a computer is attached to a domain on Linux and MacOS
        return False
    elif opersys.lower() in ("win32", "windows"):
        try:
            logger.debug(
                "Determine if computer joined to a domain using WMI through win32 API."
            )
            return _is_computer_in_domain_win32()
        except Exception as err:
            logger.error(
                f"Something went wrong using WMI through win32com. Trace: {err}. "
                "Trying with other methods..."
            )

        try:
            logger.debug("Determine if computer joined to a domain using PyAD.")
            return _is_computer_in_domain_pyad()
        except Exception as err:
            logger.error(
                f"Something went wrong using PyAD. Trace: {err}. Fallback to PowerShell..."
            )
        # fallback with PowerShell
        return _is_computer_in_domain_powershell()

    else:
        raise NotImplementedError(f"Unsupported operating system: {opersys}")


@lru_cache
def is_user_in_group(group_name: str, user_name: str | None = None) -> bool:
    """Check if a user is a member of a specified group.

    Args:
        user_name (str | None, optional): The username to check. If None, the current
            user name is used. Defaults to None.
        group_name (str): The name of the group to check membership.

    Returns:
        bool: True if the user is a member of the group, False otherwise or if
            something fails.
    """
    # local variables
    local_groups = []
    domain_groups = []

    # if user not specified, use the current user name
    if user_name is None:
        user_name = getuser()

    # first, get local groups
    try:
        local_groups = get_user_local_groups()
        logger.debug(
            f"User '{user_name}' belongs to following LOCAL groups: {'; '.join(local_groups)}. "
        )
    except Exception as err:
        logger.error(f"Retrieving user's LOCAL groups failed. Trace: {err}")

    # if computer is not attached to a domain, check only on local groups
    if not is_computer_attached_to_a_domain():
        return group_name in local_groups

    try:
        domain_groups = get_user_domain_groups()
        logger.debug(
            f"User '{user_name}' belongs to following DOMAIN groups: {'; '.join(domain_groups)}. "
        )
    except Exception as err:
        logger.error(f"Retrieving user's DOMAIN groups failed. Trace: {err}")

    return any([group_name in domain_groups, group_name in local_groups])

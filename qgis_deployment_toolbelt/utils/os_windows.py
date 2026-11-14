#! python3  # noqa: E265

"""
Utilities specific for Windows.

Author: Julien Moura (https://github.com/guts)

Inspired from py-setenv: <https://github.com/beliaev-maksim/py_setenv> (MIT)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import ctypes
import logging
from enum import Enum
from os import sep  # required since pathlib strips trailing whitespace
from pathlib import Path
from sys import platform as opersys

# package
from qgis_deployment_toolbelt.exceptions import DomainControllerUnreachableError


# Imports depending on operating system
if opersys == "win32":
    """windows"""
    # standard
    import winreg

    # 3rd party
    import pythoncom
    import win32com.client
    import win32gui
    from win32comext.shell import shell, shellcon


# #############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger(__name__)

# https://learn.microsoft.com/windows/win32/debug/system-error-codes--1300-1699-
ERROR_NO_SUCH_DOMAIN = 1355

if opersys == "win32":
    """windows"""
    system_hkey = (
        winreg.HKEY_LOCAL_MACHINE,
        r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
    )
    user_hkey = (winreg.HKEY_CURRENT_USER, r"Environment")


# #############################################################################
# ########## Classes ###############
# ##################################


class ExtendedNameFormat(Enum):
    """Possible values for user name in a Windows Active Directory context.
    See references:

    - https://learn.microsoft.com/windows/win32/api/secext/ne-secext-extended_name_format
    - https://mhammond.github.io/pywin32/win32api__GetUserNameEx_meth.html
    - https://github.com/mhammond/pywin32/blob/dde12b8ef274a157aede18f46cae5b44f112be17/win32/Lib/win32con.py#L4963-L4973

    """

    # An unknown name type.
    NameUnknown = 0
    # The fully qualified distinguished name (for example, CN=Jeff Smith,OU=Users,DC=Engineering,DC=Microsoft,DC=Com).
    NameFullyQualifiedDN = 1
    # A legacy account name (for example, Engineering\JSmith).
    # The domain-only version includes trailing backslashes (\).
    NameSamCompatible = 2
    # A "friendly" display name (for example, Jeff Smith).
    # The display name is not necessarily the defining relative distinguished name (RDN).
    NameDisplay = 3
    # A GUID string that the IIDFromString function returns (for example,
    # {4fa050f0-f561-11cf-bdd9-00aa003a77b6}).
    NameUniqueId = 6
    # The complete canonical name (for example,
    # engineering.microsoft.com/software/someone).
    # The domain-only version includes a trailing forward slash (/).
    NameCanonical = 7
    # The user principal name (for example, someone@example.com).
    NameUserPrincipal = 8
    # The same as NameCanonical except that the rightmost forward slash (/) is replaced
    # with a new line character (\n), even in a domain-only case (for example,
    # engineering.microsoft.com/software\nJSmith).
    NameCanonicalEx = 9
    # The generalized service principal name (for example,
    # www/www.microsoft.com@microsoft.com).
    NameServicePrincipal = 10
    # The DNS domain name followed by a backward-slash and the SAM user name.
    NameDnsDomain = 12
    # The first name or given name of the user. Note: This type is only available for
    # GetUserNameEx calls for an Active Directory user.
    NameGivenName = 13
    # The last name or surname of the user. Note: This type is only available for
    # GetUserNameEx calls for an Active Directory user.
    NameSurname = 14


# #############################################################################
# ########## Functions #############
# ##################################


def delete_environment_variable(envvar_name: str, scope: str = "user") -> bool:
    """Deletes environment variable.

    Args:
        envvar_name (str): environment variable name (= key) to delete
        scope (str, optional): environment variable scope. Must be "user" or "system",
            defaults to "user". Defaults to "user".

    Returns:
        bool: True is the variable has been successfully deleted
    """
    # user or system
    if scope == "user":
        hkey = user_hkey
    else:
        hkey = system_hkey

    # check that the variable exists
    if (
        get_environment_variable(
            envvar_name=envvar_name, scope=scope, log_level_if_missing=logging.DEBUG
        )
        is None
    ):
        logger.debug(
            f"Variable '{envvar_name}' not found in scope '{scope}': nothing to delete."
        )
        return False

    # if it does exist, try to delete the variable
    try:
        with winreg.OpenKey(*hkey, access=winreg.KEY_ALL_ACCESS) as key:
            winreg.DeleteValue(key, envvar_name)
            return True
    except OSError as err:
        logger.error(
            f"Delete variable '{envvar_name}' from scope '{scope}' failed. Trace: {err}"
        )
        return False


def get_environment_variable(
    envvar_name: str,
    scope: str = "user",
    *,
    log_level_if_missing: int = logging.ERROR,
) -> str | None:
    """Get environment variable from Windows registry.

    Args:
        envvar_name (str): environment variable name (= key) to retrieve
        scope (str, optional): environment variable scope. Must be "user" or "system",
            defaults to "user". Defaults to "user".
        log_level_if_missing (int, optional): logging level used when the variable
            does not exist. Defaults to logging.ERROR.

    Returns:
        Optional[str]: environment variable value or None if not found
    """
    # user or system
    if scope == "user":
        hkey = user_hkey
    else:
        hkey = system_hkey

    # try to get the value
    try:
        with winreg.OpenKey(*hkey, access=winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, envvar_name)
        return value
    except FileNotFoundError:
        logger.log(
            log_level_if_missing,
            f"Environment variable {envvar_name} not found in registry "
            f"(scope: {scope}).",
        )
        return None
    except OSError as err:
        logger.error(
            f"Environment variable {envvar_name} could not be read from registry "
            f"(scope: {scope}). Trace: {err}"
        )
        return None


def get_current_user_extended_data(extended_name_format: ExtendedNameFormat) -> str:
    """Get current user full data extended with Active Directory informations.

    This method uses the ctypes module since the upper-level method implemented in
    `pywin32.win32api` (`win32api.GetUserNameEx(extended_name_format.value)`) raises an
    error when the specified format is not reachable.

    Inspired from: https://stackoverflow.com/a/70182936/2556577

    Returns:
        str: use data in the specified format, empty if not available

    Raises:
        DomainControllerUnreachableError: domain controller unavailable

    Example:

        .. code-block:: python

            from qgis_deployment_toolbelt.utils.os_windows import (
                ExtendedNameFormat,
                get_current_user_extended_data,
            )

            user_data = {
                k.name: get_current_user_extended_data(k) for k in ExtendedNameFormat
            }

            print(user_data)

    """
    format_index = extended_name_format.value

    # use system DLL to call API, keeping its error code
    secur32 = ctypes.WinDLL("secur32", use_last_error=True)
    GetUserNameEx = secur32.GetUserNameExW  # noqa: N806
    GetUserNameEx.restype = ctypes.c_ubyte  # BOOLEAN, not the default C int

    size = ctypes.pointer(ctypes.c_ulong(0))
    GetUserNameEx(format_index, None, size)

    name_buffer = ctypes.create_unicode_buffer(size.contents.value)
    # a format not available for the user (local account) is just empty
    if (
        not GetUserNameEx(format_index, name_buffer, size)
        and ctypes.get_last_error() == ERROR_NO_SUCH_DOMAIN
    ):
        raise DomainControllerUnreachableError(extended_name_format.name)

    return name_buffer.value


def normalize_path(input_path: Path, add_trailing_slash_if_dir: bool = True) -> str:
    r"""Returns a path as normalized and fully escaped for Windows old-school file style.

    :param Path input_path: path to normalize
    :param bool add_trailing_slash_if_dir: add a trailing slash if the input is a folder,\
        defaults to True

    :return str: normalized path as string

    :example:

    .. code-block:: python

        t = Path(r'C:\Users\risor\Documents\GitHub\Geotribu\qtribu\qtribu\resources\images')
        print(normalize_path(t))
        > C:\\Users\\risor\\Documents\\GitHub\\Geotribu\\qtribu\\qtribu\\resources\\images\\

    """
    if input_path.is_dir() and add_trailing_slash_if_dir:
        return repr(str(input_path.resolve()) + sep).replace("'", "")
    else:
        return repr(str(input_path.resolve())).replace("'", "")


def refresh_environment() -> bool:
    """This ensures that changes to Windows registry are immediately propagated.
    Useful to refresh after have updated the environment variables.

    A method by Geoffrey Faivre-Malloy and Ronny Lipshitz.
    Source: https://gist.github.com/apetrone/5937002

    Returns:
        bool: True if the environment has been refreshed
    """
    # broadcast settings change
    HWND_BROADCAST: int = 0xFFFF  # noqa: N806
    WM_SETTINGCHANGE: int = 0x001A  # noqa: N806
    SMTO_ABORTIFHUNG: int = 0x0002  # noqa: N806
    send_parameter = "Environment"

    res1 = res2 = None
    try:
        res1, res2 = win32gui.SendMessageTimeout(
            HWND_BROADCAST, WM_SETTINGCHANGE, 0, send_parameter, SMTO_ABORTIFHUNG, 100
        )
    except NameError:
        logger.critical(" name 'win32gui' is not defined")
    if not res1:
        logger.warning(
            f"Refresh environment failed: {bool(res1)}, {res2}, from SendMessageTimeout"
        )
        return False
    else:
        return True


def set_environment_variable(
    envvar_name: str, envvar_value: str, scope: str = "user"
) -> bool:
    """Creates/replaces environment variable.

    Args:
        envvar_name (str): name (= key) of environment variable to set or replace.
        envvar_value (str): value to set for the environment variable
        scope (str, optional): environment variable scope. Must be "user" or "system",
            defaults to "user". Defaults to "user".

    Returns:
        bool: True is the variable has been successfully set
    """
    # user or system
    if scope == "user":
        hkey = user_hkey
    else:
        hkey = system_hkey

    # try to set the value
    try:
        with winreg.OpenKey(*hkey, access=winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, envvar_name, 0, winreg.REG_SZ, envvar_value)
        return True
    except OSError as err:
        logger.error(
            f"Set variable '{envvar_name}' with value '{envvar_value}' to "
            f"scope '{scope}' failed. Trace: {err}"
        )
        return False


def get_user_desktop_folder() -> Path:
    """Return the user Desktop folder (`CSIDL_DESKTOP`).

    Returns:
        Path: path to the current user Desktop folder.
    """
    return Path(shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0))


def get_user_home_folder() -> Path:
    """Return the user home folder.

    Note that we return `CSIDL_PROFILE`, not `CSIDL_APPDATA`, `CSIDL_LOCAL_APPDATA`
    or `CSIDL_COMMON_APPDATA`.
    See: https://www.nirsoft.net/articles/find_special_folder_location.html
    TODO: evaluate use of platformdirs

    Returns:
        Path: path to the user home
    """
    return Path(shell.SHGetFolderPath(0, shellcon.CSIDL_PROFILE, 0, 0))


def get_user_startmenu_folder() -> Path:
    """Return the user Start Menu Programs folder.

    Note that we return `CSIDL_PROGRAMS` not `CSIDL_COMMON_PROGRAMS`.

    Returns:
        Path: path to the Start Menu Programs folder
    """
    return Path(shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAMS, None, 0))


def read_shortcut(shortcut_path: Path) -> tuple[str, Path | None] | None:
    """Read the description and the working directory of a Windows shortcut.

    Args:
        shortcut_path (Path): path to the .lnk file

    Returns:
        tuple[str, Path | None] | None: description and working directory, or None
            if the shortcut can't be read
    """
    pythoncom.CoInitialize()
    win_shell = win32com.client.Dispatch("Wscript.Shell")
    try:
        # opens the shortcut if it already exists, without writing anything until
        # see: https://learn.microsoft.com/previous-versions/windows/internet-explorer/ie-developer/windows-scripting/xsy6k3ys(v=vs.84)
        wscript = win_shell.CreateShortcut(str(shortcut_path))
        description, work_dir = wscript.Description, wscript.WorkingDirectory
    except pythoncom.com_error as err:
        logger.debug(f"Unable to read shortcut {shortcut_path}: {err}")
        return None

    return description, Path(work_dir) if work_dir else None

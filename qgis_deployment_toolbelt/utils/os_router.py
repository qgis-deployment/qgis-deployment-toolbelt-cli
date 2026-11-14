#! python3
# ruff: noqa: F401

"""Just a router to functions depending on operating system."""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard
from sys import platform as opersys


__all__ = [
    "delete_environment_variable",
    "get_environment_variable",
    "get_user_desktop_folder",
    "get_user_home_folder",
    "get_user_startmenu_folder",
    "read_shortcut",
    "refresh_environment",
    "set_environment_variable",
]


if opersys == "win32":
    from qgis_deployment_toolbelt.utils.os_windows import (
        delete_environment_variable,
        get_environment_variable,
        get_user_desktop_folder,
        get_user_home_folder,
        get_user_startmenu_folder,
        read_shortcut,
        refresh_environment,
        set_environment_variable,
    )
elif opersys == "linux":
    from qgis_deployment_toolbelt.utils.os_linux import (
        delete_environment_variable,
        get_environment_variable,
        get_user_desktop_folder,
        get_user_home_folder,
        get_user_startmenu_folder,
        read_shortcut,
        refresh_environment,
        set_environment_variable,
    )
elif opersys == "darwin":
    from qgis_deployment_toolbelt.utils.os_mac import (
        get_user_desktop_folder,
        get_user_home_folder,
        get_user_startmenu_folder,
    )

    delete_environment_variable = None
    get_environment_variable = None
    read_shortcut = None
    refresh_environment = None
    set_environment_variable = None
else:
    delete_environment_variable = None
    get_environment_variable = None
    get_user_desktop_folder = None
    get_user_home_folder = None
    get_user_startmenu_folder = None
    read_shortcut = None
    refresh_environment = None
    set_environment_variable = None

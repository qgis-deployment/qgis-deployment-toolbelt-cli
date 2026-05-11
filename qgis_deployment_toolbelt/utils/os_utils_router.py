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
    "refresh_environment",
    "set_environment_variable",
]


if opersys == "win32":
    from qgis_deployment_toolbelt.utils.win32utils import (
        delete_environment_variable,
        get_environment_variable,
        refresh_environment,
        set_environment_variable,
    )
elif opersys == "linux":
    from qgis_deployment_toolbelt.utils.linux_utils import (
        delete_environment_variable,
        get_environment_variable,
        refresh_environment,
        set_environment_variable,
    )
else:
    delete_environment_variable = None
    get_environment_variable = None
    refresh_environment = None
    set_environment_variable = None

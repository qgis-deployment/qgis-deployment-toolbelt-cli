#! python3  # noqa: E265

"""
Custom INI files interpolation.

Author: Julien Moura (https://github.com/guts)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from collections import ChainMap
from configparser import BasicInterpolation, ConfigParser, InterpolationSyntaxError
from os.path import expanduser, expandvars


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)

# #############################################################################
# ########## Classes ###############
# ##################################


class EnvironmentVariablesInterpolation(BasicInterpolation):
    """Custom interpolation to handle environment variables in ini files.

    Inspired from https://gist.github.com/malexer/ee2f93b1973120925e8beb3f36b184b8.


    Example:

        .. code-block:: ini

            [test]
            user = $USER
            user_home = $HOME
            fake_value_from_environment_variable = $QDT_TEST_ENV_VARIABLE
            pictures = %(user_home)s/.cache/qgis-deployment-toolbelt
    """

    def before_get(
        self,
        parser: ConfigParser,
        section: str,
        option: str,
        value: str,
        defaults: ChainMap,
    ) -> str:
        """Called for every get option=value line in INI file.

        Args:
            parser (ConfigParser): parser whose function is overloaded
            section (str): section's name
            option (str): option's name
            value (str): value to try to interpolate
            defaults (ChainMap): defaults options/values

        Returns:
            str: interpolated value
        """
        # Add try catch because QGIS INI file can omit some % escaping
        try:
            value = super().before_get(parser, section, option, value, defaults)
        except InterpolationSyntaxError:
            return value

        try:
            return expandvars(expanduser(value))  # noqa: PTH111
        except Exception as exc:
            logger.error(
                f"Failed to interpolate {value} in {section}/{option}. Trace: {exc}"
            )
            return value

    def before_set(
        self,
        parser: ConfigParser,
        section: str,
        option: str,
        value: str,
    ) -> str:
        """Called for every set option=value line in INI file.

        Args:
            parser (ConfigParser): parser whose function is overloaded
            section (str): section's name
            option (str): option's name
            value (str): value to try to interpolate
        Returns:
            str: interpolated value
        """
        # Add try catch because QGIS INI file can omit some % escaping
        try:
            return super().before_set(parser, section, option, value)
        except (InterpolationSyntaxError, ValueError):
            return value

    def before_write(
        self,
        parser: ConfigParser,
        section: str,
        option: str,
        value: str,
    ) -> str:
        """Called before write option=value line in INI file.

        Args:
            parser (ConfigParser): parser whose function is overloaded
            section (str): section's name
            option (str): option's name
            value (str): value to try to interpolate

        Returns:
            str: interpolated value
        """
        value = super().before_write(parser, section, option, value)
        try:
            return expandvars(expanduser(value))  # noqa: PTH111
        except Exception as exc:
            logger.error(
                f"Failed to interpolate {value} in {section}/{option}. Trace: {exc}"
            )
            return value


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    pass

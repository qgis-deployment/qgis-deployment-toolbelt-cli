#! python3  # noqa: E265

"""
Read and write QGIS configuration files.

Author: Julien Moura (https://github.com/guts)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# special
from __future__ import annotations

# Standard library
import logging
from pathlib import Path
from typing import Literal

# package
from qgis_deployment_toolbelt.utils.check_path import check_path
from qgis_deployment_toolbelt.utils.ini_interpolation import (
    EnvironmentVariablesInterpolation,
)
from qgis_deployment_toolbelt.utils.ini_parser_with_path import CustomConfigParser
from qgis_deployment_toolbelt.utils.win32utils import normalize_path


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)

# #############################################################################
# ########## Classes ###############
# ##################################


class QgisIniHelper:
    """Helper to manipulate QGIS configuration files (*.ini)."""

    SUPPORTED_INI_TYPES: tuple[str, str, str] = (
        "plugin_metadata",
        "profile_qgis3",
        "profile_qgis3customization",
    )

    ini_type: str | None = None

    def __init__(
        self,
        ini_filepath: Path,
        ini_type: Literal[
            "profile_qgis3", "profile_qgis3customization", "plugin_metadata", None
        ] = None,
        strict: bool = False,
        enable_environment_variables_interpolation: bool = True,
    ) -> None:
        """Instanciation.

        Args:
            ini_filepath (Path): path to the QGIS3.ini configuration file
            ini_type (Literal[ &quot;profile_qgis3&quot;, \
                &quot;profile_qgis3customization&quot;, &quot;plugin_metadata&quot;, \
                None ], optional): type of ini file. None enables autodetection. \
                Defaults to None.
            strict (bool, optional): strict mode applied to ConfigParser. Defaults to \
                False.
            enable_environment_variables_interpolation (bool, optional): if enabled, \
                values matching environment variables are interepreted. Defaults to True.
        """
        if (
            ini_filepath is not None
            and ini_type is not None
            and ini_type in self.SUPPORTED_INI_TYPES
        ):
            self.ini_type = ini_type
            if self.ini_type == "profile_qgis3":
                self.profile_config_path = ini_filepath
                self.profile_customization_path = ini_filepath.with_name(
                    "QGISCUSTOMIZATION3.ini"
                )
            elif self.ini_type == "profile_qgis3customization":
                self.profile_config_path = ini_filepath.with_name("QGIS3.ini")
                self.profile_customization_path = ini_filepath
            else:
                self.profile_config_path = None
                self.profile_customization_path = None
        elif ini_filepath.stem == "QGIS3":
            self.ini_type = "profile_qgis3"
            self.profile_config_path = ini_filepath
            self.profile_customization_path = ini_filepath.with_name(
                "QGISCUSTOMIZATION3.ini"
            )
        elif ini_filepath.stem == "QGISCUSTOMIZATION3":
            self.ini_type = "profile_qgis3customization"
            self.profile_config_path = ini_filepath.with_name("QGIS3.ini")
            self.profile_customization_path = ini_filepath
        elif ini_filepath.name == "metadata.txt":
            self.ini_type = "plugin_metadata"
            self.profile_config_path = None
            self.profile_customization_path = None
        else:
            logger.warning(f"Unrecognized ini type: {ini_filepath}")

        # check if file exists
        if not check_path(
            input_path=ini_filepath,
            must_be_a_file=True,
            must_be_readable=True,
            must_exists=True,
            raise_error=False,
        ):
            logger.info(f"The specified file does not exist: {ini_filepath.resolve()}.")
        self.ini_filepath = ini_filepath

        # store options
        self.strict_mode = strict
        self.enable_environment_variables_interpolation = (
            enable_environment_variables_interpolation
        )

    def cfg_parser(self) -> CustomConfigParser:
        """Return config parser with options for QGIS ini files.

        Returns:
            CustomConfigParser: config parser
        """
        qgis_cfg_parser = CustomConfigParser(
            strict=self.strict_mode,
            interpolation=(
                EnvironmentVariablesInterpolation()
                if self.enable_environment_variables_interpolation
                else None
            ),
        )
        qgis_cfg_parser.optionxform = str
        return qgis_cfg_parser

    # UI customization
    def is_ui_customization_enabled(
        self, ini_file: CustomConfigParser | Path | None = None
    ) -> bool | None:
        """Determine if UI customization is enabled.

        Args:
            ini_file (Union[CustomConfigParser, Path]): input ini file to check.
                A warning is raised if the filename is not QGIS3.ini.
                If None, self.profile_config_path is used.

        Returns:
            bool: True if customization is enabled
        """
        if ini_file is None and isinstance(self.profile_config_path, Path):
            logger.debug(
                "Using configuration file defined at object level: "
                f"{self.profile_config_path.resolve()}"
            )
            return self.is_ui_customization_enabled(ini_file=self.profile_config_path)

        if self.ini_type not in ("profile_qgis3", "profile_qgis3customization"):
            logger.debug(
                f"Invalid ini type: {self.ini_type}. Must a QGIS3.ini or a QGIS3CUSTOMIZATION.ini"
            )
            return None

        if isinstance(ini_file, CustomConfigParser):
            if ini_file.has_option(section="UI", option="Customization\\enabled"):
                return ini_file.getboolean(
                    section="UI", option="Customization\\enabled"
                )
            else:
                return False
        elif isinstance(ini_file, Path):
            if ini_file.stem == "QGIS3":
                logger.warning(
                    "Input file does not seem to be a QGIS profile configuration file "
                    f"(QGIS/QGIS3.ini): {ini_file}"
                )

            cfg_parser = self.cfg_parser()
            cfg_parser.read(ini_file, encoding="UTF8")
            return self.is_ui_customization_enabled(cfg_parser)
        elif (
            ini_file is None
            and isinstance(self.profile_config_path, Path)
            and self.profile_config_path.exists()
        ):
            cfg_parser = self.cfg_parser()
            cfg_parser.read([self.profile_config_path], encoding="UTF8")
            return self.is_ui_customization_enabled(cfg_parser)
        else:
            return False

    def is_splash_screen_set(
        self, ini_file: CustomConfigParser | Path | None = None
    ) -> bool | None:
        """Determine if a custom splash screen is set or not.

        Args:
            ini_file (Union[CustomConfigParser, Path]): input ini file to check.
                A warning is raised if the filename is not QGISCUSTOMIZATION3.ini.
                If None, self.profile_customization_path is used.

        Returns:
            bool: True if a splash is set
        """
        # if ini_file is None but defined at object level, let's use it
        if ini_file is None and isinstance(self.profile_customization_path, Path):
            logger.debug(
                "Using customization file defined at object level: "
                f"{self.profile_customization_path.resolve()}"
            )
            return self.is_splash_screen_set(ini_file=self.profile_customization_path)

        if isinstance(ini_file, CustomConfigParser):
            if ini_file.has_option(section="Customization", option="splashpath"):
                splash_path = ini_file.get(section="Customization", option="splashpath")
                if isinstance(splash_path, str) and not len(splash_path.strip()):
                    logger.info(
                        f"{ini_file.get_initial_file_path().resolve()} has a splashpath "
                        "option BUT the value set is NOT a valid path"
                    )
                    return False
                else:
                    logger.debug(
                        f"{ini_file.initial_file_path} has a splash screen set: {splash_path}"
                    )
                    return True
            else:
                logger.debug(
                    f"{ini_file.get_initial_file_path().resolve()} has no splash path set."
                )
                return False
        elif isinstance(ini_file, Path) and check_path(
            input_path=ini_file,
            must_be_a_file=True,
            must_be_readable=True,
            must_exists=True,
            raise_error=False,
        ):
            cfg_parser = self.cfg_parser()
            cfg_parser.read(ini_file, encoding="UTF8")
            logger.debug(
                f"{ini_file} is an existing file and has been parsed. Let's check if a "
                "splash path is set."
            )
            return self.is_splash_screen_set(cfg_parser)
        else:
            return False

    def set_ui_customization_enabled(self, switch: bool = True) -> bool:
        """Enable/disable UI customization in the profile QGIS3.ini file.

        Args:
            switch (bool, optional): True to enable, False to disable UI customization.
                Defaults to True.

        Returns:
            bool: UI customization state. True is enabled, False is disabled.
        """
        # local variables
        section = "UI"
        option = "Customization\\enabled"

        # boolean syntax for PyQt
        switch_value = "false"
        if switch:
            switch_value = "true"

        # make sure that the file exists
        if not self.profile_config_path.exists():
            logger.warning(
                f"Configuration file {self.profile_config_path} doesn't exist. "
                "It will be created but maybe it was not the expected behavior."
            )
            self.profile_config_path.touch(exist_ok=True)
            self.profile_config_path.write_text(
                data=f"[UI]\nCustomization\\enabled={switch_value}", encoding="UTF8"
            )
            return switch

        # read configuration file
        ini_qgis3 = self.cfg_parser()
        ini_qgis3.read(self.profile_config_path, encoding="UTF8")

        # if section and option already exist
        if ini_qgis3.has_option(section=section, option=option):  # = section AND option
            actual_state = ini_qgis3.getboolean(section=section, option=option)
            # when actual UI customization is enabled
            if actual_state and switch:
                logger.debug(
                    f"UI Customization is already ENABLED in {self.profile_config_path}"
                )
                return True
            elif actual_state and not switch:
                ini_qgis3.set(
                    section=section,
                    option=option,
                    value=switch_value,
                )
                with self.profile_config_path.open("w", encoding="UTF8") as configfile:
                    ini_qgis3.write(configfile, space_around_delimiters=False)
                logger.debug(
                    "UI Customization was ENABLED and has been "
                    f"DISABLED in {self.profile_config_path}"
                )
                return False

            # when actual UI customization is disabled
            elif not actual_state and switch:
                ini_qgis3.set(
                    section=section,
                    option=option,
                    value=switch_value,
                )
                with self.profile_config_path.open("w", encoding="UTF8") as configfile:
                    ini_qgis3.write(configfile, space_around_delimiters=False)
                logger.debug(
                    "UI Customization was DISABLED and has been "
                    f"ENABLED in {self.profile_config_path}"
                )
                return True
            elif not actual_state and not switch:
                logger.debug(
                    f"UI Customization is already DISABLED in {self.profile_config_path}"
                )
                return True
        elif ini_qgis3.has_section(section=section) and switch:
            # section exist but not the option, so let's add it as required
            ini_qgis3.set(
                section=section,
                option=option,
                value=switch_value,
            )
            with self.profile_config_path.open("w", encoding="UTF8") as configfile:
                ini_qgis3.write(configfile, space_around_delimiters=False)
            logger.debug(
                f"'{option}' option was missing in {section}, it's just been added and "
                f"ENABLED in {self.profile_config_path}"
            )
            return True
        elif not ini_qgis3.has_section(section=section) and switch:
            # even the section is missing. Let's add everything
            ini_qgis3.add_section(section)
            ini_qgis3.set(
                section=section,
                option=option,
                value=switch_value,
            )
            with self.profile_config_path.open("w", encoding="UTF8") as configfile:
                ini_qgis3.write(configfile, space_around_delimiters=False)
            logger.debug(
                f"'{option}' option was missing in {section}, it's just been added and "
                f"ENABLED in {self.profile_config_path}"
            )
            return True
        else:
            logger.debug(
                f"Section '{section}' is not present so {option} is DISABLED in "
                f"{self.profile_config_path}"
            )
            return False

    def set_splash_screen(
        self,
        ini_file: CustomConfigParser | Path | None = None,
        splash_screen_filepath: Path | None = None,
        switch: bool = True,
    ) -> bool:
        """Add/remove splash screen path to the QGISCUSTOMIZATION3.ini file.

        Args:
            ini_file (Union[CustomConfigParser, Path]): input ini file to check.
                A warning is raised if the filename is not QGISCUSTOMIZATION3.ini.
                If None, self.profile_customization_path is used.
            splash_screen_filepath (Path, optional): path to the folder containing the
                splash.png file, defaults to None. Defaults to None.
            switch (bool, optional): True to add, False to remove, defaults to True.
                Defaults to True.

        Returns:
            bool: True is the splash folder is present. False is absent.
        """
        # if ini_file is None but defined at object level, let's use it
        if ini_file is None and isinstance(self.profile_customization_path, Path):
            logger.debug(
                "Using customization file defined at object level: "
                f"{self.profile_customization_path.resolve()}"
            )
            return self.set_splash_screen(
                ini_file=self.profile_customization_path, switch=switch
            )
        elif ini_file is None and self.profile_customization_path is None:
            raise ValueError(
                "Both passed ini file and the object's defined are not defined. Can't process."
            )

        # SWITCH=False and NOT DEFINED --> EXIT
        if not switch and not self.is_splash_screen_set(ini_file=ini_file):
            logger.debug(
                f"As required ({switch=}, splash screen is not set in {ini_file}"
            )
            return False

        # SWITCH=TRUE --> ENABLE
        if switch and isinstance(splash_screen_filepath, Path):
            # normalize splash screen folder path
            nrm_splash_screen_folder = normalize_path(
                splash_screen_filepath.parent, add_trailing_slash_if_dir=True
            )
            logger.debug(
                f"Splash screen path has been normalized: {nrm_splash_screen_folder}"
            )
        elif switch and splash_screen_filepath is None:
            logger.warning(f"{switch=} but splash screen filepath not defined")
        else:
            pass

        # make sure that the file exists
        if isinstance(ini_file, Path) and ini_file.exists():
            # open
            cfg_parser = self.cfg_parser()
            cfg_parser.read(ini_file, encoding="UTF8")
            logger.debug(
                f"{ini_file} is an existing file, has been parsed. Let's check if a "
                "splash path is set."
            )
            return self.set_splash_screen(
                ini_file=cfg_parser,
                splash_screen_filepath=splash_screen_filepath,
                switch=switch,
            )
        elif isinstance(ini_file, Path) and not ini_file.exists() and switch:
            logger.warning(
                f"Configuration file {ini_file} doesn't exist. "
                "It will be created but maybe it was not the expected behavior."
            )
            ini_file.parent.mkdir(parents=True, exist_ok=True)
            ini_file.touch(exist_ok=True)
            ini_file.write_text(
                data=f"[Customization]\nsplashpath={nrm_splash_screen_folder}",
                encoding="UTF8",
            )
            return switch
        elif isinstance(ini_file, Path) and not ini_file.exists() and not switch:
            logger.debug(f"'{ini_file} doesn't exist. So, no need to do anything.")
            return switch
        else:
            pass

        # FROM NOW: isinstance(ini_file, CustomConfigParser) is True
        qgiscustomization3ini_filepath = ini_file.get_initial_file_path()
        option = "splashpath"
        section = "Customization"

        # check existing option value
        if ini_file.has_option(section=section, option=option):
            actual_state = ini_file.get(section=section, option=option)

            if not switch:
                ini_file.remove_option(section=section, option=option)
                with qgiscustomization3ini_filepath.open(
                    "w", encoding="UTF8"
                ) as configfile:
                    ini_file.write(configfile, space_around_delimiters=False)
                logger.debug(
                    f"Splash screen {splash_screen_filepath} has been "
                    f"DISABLED in {qgiscustomization3ini_filepath}"
                )
                return True
            elif actual_state == nrm_splash_screen_folder and switch:
                logger.debug(
                    f"Splash screen {splash_screen_filepath} is already "
                    f"ENABLED in {qgiscustomization3ini_filepath}"
                )
                return True
            elif actual_state != nrm_splash_screen_folder and switch:
                ini_file.set(
                    section=section,
                    option=option,
                    value=nrm_splash_screen_folder,
                )
                with qgiscustomization3ini_filepath.open(
                    "w", encoding="UTF8"
                ) as configfile:
                    ini_file.write(configfile, space_around_delimiters=False)
                logger.debug(
                    f"Splash screen {splash_screen_filepath} has been "
                    f"ENABLED in {qgiscustomization3ini_filepath}"
                )
                return True
            else:
                pass

        elif ini_file.has_section(section=section) and switch:
            # section exist but not the option, so let's add it as required
            ini_file.set(
                section=section,
                option=option,
                value=nrm_splash_screen_folder,
            )
            with qgiscustomization3ini_filepath.open(
                "w", encoding="UTF8"
            ) as configfile:
                ini_file.write(configfile, space_around_delimiters=False)
            logger.debug(
                f"'{option}' option was missing in {section}, it's just been added and "
                f"ENABLED in {qgiscustomization3ini_filepath}"
            )
            return True
        elif not ini_file.has_section(section=section) and switch:
            # even the section is missing. Let's add everything
            ini_file.add_section(section)
            ini_file.set(
                section=section,
                option=option,
                value=nrm_splash_screen_folder,
            )
            with qgiscustomization3ini_filepath.open(
                "w", encoding="UTF8"
            ) as configfile:
                ini_file.write(configfile, space_around_delimiters=False)
            logger.debug(
                f"'{option}' option was missing in {section}, it's just been added and "
                f"ENABLED in {qgiscustomization3ini_filepath}"
            )
            return True
        else:
            logger.debug(
                f"Section '{section}' is not present so "
                f"{option} is DISABLED in {qgiscustomization3ini_filepath}"
            )
            return False

    @staticmethod
    def _copy_section(
        config_dest: CustomConfigParser,
        config_src: CustomConfigParser,
        section_src: str,
    ) -> None:
        """Copy section from an INI config to another INI config

        Args:
            config_dest (CustomConfigParser): destination INI content
            config_src (CustomConfigParser): source INI content
            section_src (str): section to copy
        """
        if section_src not in config_dest.sections() and section_src != "DEFAULT":
            config_dest.add_section(section_src)
        for param in config_src[section_src]:
            config_dest[section_src][param] = config_src[section_src][param]

    @staticmethod
    def _backup_section(
        config_dest: CustomConfigParser,
        config_src: CustomConfigParser,
        section_src: str,
        dst: Path,
    ) -> None:
        """Backup a INI section for with updated values

        Args:
            config_dest (CustomConfigParser): destination INI content
            config_src (CustomConfigParser): source INI content
            section_src (str): section to backup
            dst (Path): destination file
        """
        if section_src not in config_dest:
            return
        # Get updated values
        updated_values = {
            param: config_dest[section_src][param]
            for param in config_src[section_src]
            if param in config_dest[section_src]
            and config_src[section_src][param] != config_dest[section_src][param]
        }
        if len(updated_values):
            backup_section = f"QDT_backup_{section_src}"
            logger.info(
                f"Section {section_src} already available in {dst}. Copying updated content to {backup_section}"
            )
            if backup_section not in config_dest.sections():
                config_dest.add_section(backup_section)
            for param, backup_val in updated_values.items():
                config_dest[backup_section][param] = backup_val

    def merge_to(self, dst: QgisIniHelper) -> None:
        """Merge INI file to another INI file.
        If the destination file exists a merge is done:
        - all available sections are kept
        - if a section is available in both INI files, keep updated parameters in a backup section
        If environnement variable interpolation is enabled, value are written with current environnement values

        Args:
            dst (QgisIniHelper): destination ini file
        """
        if not self.ini_filepath or not self.ini_filepath.exists():
            logger.warning(
                f"File {self.ini_filepath} doesn't exists. Can't merge to {dst}"
            )
            return

        # Read source INI content
        config_src = self.cfg_parser()
        config_src.read(self.ini_filepath)

        if dst.ini_filepath.exists():
            # Read destination INI content
            config_dest = dst.cfg_parser()
            config_dest.read(dst.ini_filepath)
            # Add sections in source INI
            for section in config_src:
                self._backup_section(config_dest, config_src, section, dst.ini_filepath)
                self._copy_section(config_dest, config_src, section)
            # Write to destination, environnement variable will be interpolated if interpolation enabled
            with dst.ini_filepath.open(mode="w", encoding="UTF-8") as config_file:
                config_dest.write(config_file)
        else:
            with dst.ini_filepath.open(mode="w", encoding="UTF-8") as config_file:
                config_src.write(config_file)


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    pass

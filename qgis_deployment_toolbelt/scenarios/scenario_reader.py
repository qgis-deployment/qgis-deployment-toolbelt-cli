#! python3  # noqa: E265

"""
Read and validate scenario files.

Author: Julien Moura (https://github.com/guts, Oslandia)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from io import BufferedIOBase
from pathlib import Path

# 3rd party
import yaml

# package
from qgis_deployment_toolbelt.utils.check_path import check_path


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################


class ScenarioReader:
    """Read and validate scenario files."""

    scenario: dict | None = None

    def __init__(self, in_yaml: str | Path | BufferedIOBase):
        """Instanciajeting YAML scenario reader.

        Args:
            in_yaml (str | Path | BufferedIOBase): input YAML file. Can be a path
                (as str or pathlib.Path) or an opened file.

        Raises:
            TypeError: unsupported
        """
        # check and get YAML path
        if isinstance(in_yaml, (str, Path)):
            self.input_yaml = self.check_yaml_file(in_yaml)
            # extract data from input file
            with self.input_yaml.open(mode="r", encoding="UTF-8") as bytes_data:
                self.scenario = yaml.safe_load(bytes_data)
        elif isinstance(in_yaml, BufferedIOBase):
            self.input_yaml = self.check_yaml_buffer(in_yaml)
            # extract data from input file
            self.scenario = yaml.safe_load(self.input_yaml)
        else:
            raise TypeError(
                f"Unsupported data type. Expects a str, Path or buffered IO. Got: {type(in_yaml)}"
            )

    # -- CHECKS --
    def check_yaml_file(self, yaml_path: str | Path) -> Path:
        """Perform some checks on passed yaml file and load it as Path object.

        Args:
            yaml_path (str | Path): path to the yaml file to check

        Raises:
            yaml.YAMLError: if YAML is not readable or invalid
            Exception: unhandled error

        Returns:
            Path: sanitized yaml path
        """
        # if path as string load it in Path object
        check_path(
            input_path=yaml_path,
            must_be_a_file=True,
            must_exists=True,
            must_be_readable=True,
        )
        yaml_path = Path(yaml_path)

        # check integrity and structure
        with yaml_path.open(mode="r", encoding="UTF-8") as in_yaml_file:
            try:
                yaml.safe_load_all(in_yaml_file)
            except yaml.YAMLError as exc:
                logger.error(msg=f"YAML file is invalid: {yaml_path.resolve()}")
                raise exc
            except Exception as exc:
                logger.error(
                    f"Something went wrong when reading the scenario file: {yaml_path}. "
                    f"Maybe the structure of YAML file is incorrect? Trace: {exc}"
                )
                raise exc

        # return sanitized path
        return yaml_path

    def check_yaml_buffer(self, yaml_buffer: BufferedIOBase) -> BufferedIOBase:
        """Perform some checks on passed yaml file.

        Args:
            yaml_buffer (BufferedIOBase): bytes reader of the yaml file to check

        Raises:
            yaml.YAMLError: if YAML is not readable or invalid
            Exception: unhandled error

        Returns:
            BufferedIOBase: checked bytes object
        """

        # check integrity
        try:
            yaml.safe_load_all(yaml_buffer)
        except yaml.YAMLError as exc:
            logger.error(f"Invalid YAML {yaml_buffer}. Trace: {exc}")
            raise exc
        except Exception as exc:
            logger.error(
                f"Something went wrong when reading the scenario file. "
                f"Maybe the structure of YAML file is incorrect? Trace: {exc}"
            )
            raise exc

        # return sanitized path
        return yaml_buffer

    def validate_scenario(self) -> tuple[bool, list[str] | None]:
        """Validate scenario file.

        Returns:
            True if scenario is valid, False otherwise and a
            report of validation errors (which is None if the scenario is valid).
        """
        # variables
        required_root_keys: tuple = ("metadata", "settings", "steps")

        # outputs
        valid: bool = True
        report: list[str] = []

        # check if scenario is a dict
        if not isinstance(self.scenario, dict):
            report.append(f"Scenario is not a dict but {type(self.scenario)}")
            valid = False

        # check scenario basic structure
        if any([i not in self.scenario for i in required_root_keys]):
            report.append(
                "Some of required root keys are missing: {}".format(
                    ", ".join(required_root_keys)
                )
            )
            valid = False

        # check if metadata is a dict
        if not isinstance(self.metadata, dict):
            report.append(f"Metadata is not a dict: {self.metadata}")
            valid = False

        return valid, report

    @property
    def metadata(self) -> dict | None:
        """Get metadata from scenario.

        Returns:
            metadata if it does exist
        """
        if isinstance(self.scenario, dict):
            return self.scenario.get("metadata")

    @property
    def settings(self) -> dict | None:
        """Get scenario settings from scenario.

        Returns:
            settings section if it does exist
        """
        if isinstance(self.scenario, dict):
            return self.scenario.get("settings")

    @property
    def steps(self) -> list[dict] | None:
        """Get steps from scenario.

        Returns:
            list of scenario's steps
        """
        if isinstance(self.scenario, dict):
            return self.scenario.get("steps")

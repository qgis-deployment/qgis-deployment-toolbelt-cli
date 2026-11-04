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
from typing import Any, TextIO

# 3rd party
import yaml
from packaging.version import InvalidVersion, Version

# package
from qgis_deployment_toolbelt.__about__ import __version_clean__
from qgis_deployment_toolbelt.constants import SCENARIO_REQUIRED_METADATA_KEYS
from qgis_deployment_toolbelt.exceptions import InvalidScenarioError
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
            TypeError: unsupported input type
            InvalidScenarioError: if the content is not valid YAML or the file is not
                UTF-8 encoded
        """
        # check and get YAML path
        if isinstance(in_yaml, (str, Path)):
            self.input_yaml = self.check_yaml_file(in_yaml)
            # extract data from input file
            with self.input_yaml.open(mode="r", encoding="UTF-8") as bytes_data:
                self.scenario = self._parse_yaml(
                    stream=bytes_data, source=self.input_yaml
                )
        elif isinstance(in_yaml, BufferedIOBase):
            self.input_yaml = self.check_yaml_buffer(in_yaml)
            # extract data from input file
            self.scenario = self._parse_yaml(
                stream=self.input_yaml,
                source=getattr(in_yaml, "name", type(in_yaml).__name__),
            )
        else:
            raise TypeError(
                f"Unsupported data type. Expects a str, Path or buffered IO. Got: {type(in_yaml)}"
            )

    @staticmethod
    def _parse_yaml(stream: TextIO | BufferedIOBase, source: Path | str) -> Any:
        """Parse a YAML stream, turning parsing errors into InvalidScenarioError.

        Args:
            stream (TextIO | BufferedIOBase): opened YAML file or bytes buffer
            source (Path | str): path or name of the scenario, for the message

        Raises:
            InvalidScenarioError: on YAML syntax error or text decoding error.
                The original error is chained (__cause__).

        Returns:
            Any: parsed content. Its structure is checked by validate_scenario().
        """
        try:
            return yaml.safe_load(stream)
        except UnicodeDecodeError as err:
            # typically a file saved with a legacy encoding (ANSI, cp1252...)
            raise InvalidScenarioError(
                scenario_path=source, reason=f"file is not UTF-8 encoded. {err}"
            ) from err
        except yaml.YAMLError as err:
            raise InvalidScenarioError(scenario_path=source, reason=str(err)) from err

    # -- CHECKS --
    def check_yaml_file(self, yaml_path: str | Path) -> Path:
        """Perform some checks on passed yaml file and load it as Path object.

        Args:
            yaml_path (str | Path): path to the yaml file to check

        Raises:
            OSError: if the path does not exist, is not a file or is not readable
            ValueError: if the path is invalid

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
        return Path(yaml_path)

    def check_yaml_buffer(self, yaml_buffer: BufferedIOBase) -> BufferedIOBase:
        """Perform some checks on passed yaml buffer.

        Args:
            yaml_buffer (BufferedIOBase): bytes reader of the yaml file to check

        Raises:
            ValueError: if the buffer is closed or not readable

        Returns:
            BufferedIOBase: checked bytes object
        """
        if yaml_buffer.closed or not yaml_buffer.readable():
            raise ValueError(f"YAML buffer is closed or not readable: {yaml_buffer}")

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
            return False, [f"Scenario is not a dict but {type(self.scenario)}"]

        # check scenario basic structure
        if any([i not in self.scenario for i in required_root_keys]):
            report.append(
                "Some of required root keys are missing: {}".format(
                    ", ".join(required_root_keys)
                )
            )
            valid = False

        # an empty settings section = no settings
        if self.settings is not None and not isinstance(self.settings, dict):
            report.append(
                f"Settings must be a mapping, not {type(self.settings).__name__}."
            )
            valid = False

        if "steps" in self.scenario:
            if not isinstance(self.steps, list):
                report.append(
                    f"Steps must be a list of jobs, not {type(self.steps).__name__}."
                )
                valid = False
            elif not self.steps:
                report.append("Steps must contain at least one job.")
                valid = False
            elif not all(
                isinstance(step, dict)
                and isinstance(step.get("uses"), str)
                and step["uses"].strip()
                for step in self.steps
            ):
                report.append(
                    "Each step must be a mapping with a non-empty 'uses' value."
                )
                valid = False

        # check if metadata is a dict
        if not isinstance(self.metadata, dict):
            report.append(f"Metadata is not a dict: {self.metadata}")
            valid = False
        else:
            # keys required by docs/schemas/scenario/metadata.json
            missing_keys = [
                key
                for key in SCENARIO_REQUIRED_METADATA_KEYS
                if not isinstance(self.metadata.get(key), str)
                or not self.metadata[key].strip()
            ]
            if missing_keys:
                report.append(
                    "Some of required metadata keys are missing or empty: "
                    f"{', '.join(missing_keys)}"
                )
                valid = False

            if "qdt_min_version" in self.metadata:
                is_compatible, compat_error = self.is_qdt_version_compatible()
                if not is_compatible:
                    report.append(compat_error)
                    valid = False

        return valid, report

    def is_qdt_version_compatible(self) -> tuple[bool | None, str | None]:
        """Check if the running QDT version satisfies the scenario's
        `qdt_min_version` metadata (if set).

        Returns:
            tuple[bool | None, str | None]: a tuple with a boolean (True if the
                running QDT version is compatible, False if it's too old, None if
                the comparison could not be performed) and an explicit message
                (None if compatible).
        """
        if not isinstance(self.metadata, dict):
            return None, "Metadata is not a dict, unable to check qdt_min_version."

        qdt_min_version = self.metadata.get("qdt_min_version")
        if not qdt_min_version:
            return True, None

        try:
            required_version = Version(str(qdt_min_version))
        except InvalidVersion as err:
            return (
                None,
                "Scenario metadata 'qdt_min_version' is not a valid version: "
                f"{qdt_min_version}. Trace: {err}",
            )

        try:
            running_version = Version(__version_clean__)
        except InvalidVersion as err:
            logger.warning(
                f"Unable to parse running QDT version ({__version_clean__}) to "
                f"check compatibility with scenario's qdt_min_version. Trace: {err}"
            )
            return True, None

        if running_version < required_version:
            return (
                False,
                "This scenario requires QGIS Deployment Toolbelt "
                f">= {required_version}, but the running version is "
                f"{running_version}. Please upgrade QDT.",
            )

        return True, None

    @property
    def metadata(self) -> dict | None:
        """Get metadata from scenario.

        Returns:
            metadata if it does exist
        """
        if isinstance(self.scenario, dict):
            return self.scenario.get("metadata")

    @property
    def summary(self) -> str | None:
        """Build a one-line summary of the scenario from its metadata.

        Returns:
            Summary like `"<title> (<id>). <description>"`, or None if the scenario
            has no metadata dict.
        """
        metadata = self.metadata
        if not isinstance(metadata, dict):
            return None

        summary = f"{metadata.get('title', '')} ({metadata.get('id', '')})."
        description = metadata.get("description")
        if isinstance(description, str) and description.strip():
            summary = f"{summary} {description.strip()}"
        return summary

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

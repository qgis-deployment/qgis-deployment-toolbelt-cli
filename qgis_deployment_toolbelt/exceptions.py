#! python3  # noqa: E265

"""Custom exceptions."""

# standard library
from collections.abc import Iterable
from pathlib import Path

# package
from qgis_deployment_toolbelt.utils.check_image_size import get_image_size


class JobOptionBadNameError(KeyError):
    """When a job reveives an option which is not part of accepted ones."""

    def __init__(
        self, job_id: str, bad_option_name: str, expected_options_names: Iterable[str]
    ):
        """Initialization method.

        Args:
            job_id (str): job ID
            bad_option_name (str): name of bad option passed
            expected_options_names (Iterable[str]): _description_
        """
        self.message = (
            f"Job: {job_id}. Option '{bad_option_name}' is not valid. "
            f"Valid options are: {','.join(expected_options_names)}"
        )

        super().__init__(self.message)


class JobOptionBadValueError(ValueError):
    """When a job's option reveives a value which does not complies with condition."""

    def __init__(
        self,
        job_id: str,
        bad_option_name: str,
        bad_option_value: str,
        condition: str,
        accepted_values: Iterable[str],
    ):
        """Initialization method.

        Args:
            job_id (str): job ID
            bad_option_name (str): name of bad option passed
            bad_option_type (str): name of bad option passed
            condition (str): condition
            accepted_values (Iterable[str]): accepted types of values
        """
        self.message = (
            f"Job: {job_id}. Option '{bad_option_name}' 's value '{bad_option_value}' "
            f"does not comply with condition {condition}. "
            f"Accepted pattern: {','.join(accepted_values)}"
        )

        super().__init__(self.message)


class JobOptionBadValueTypeError(TypeError):
    """When a job reveives an option which is not of the expected type."""

    def __init__(
        self,
        job_id: str,
        bad_option_name: str,
        bad_option_value: str,
        expected_option_type: Iterable[str],
    ):
        """Initialization method.

        Args:
            job_id (str): job ID
            bad_option_name (str): name of bad option passed
            bad_option_value (str): option's value
            expected_option_type (Iterable[str]): accepted types of values
        """
        self.message = (
            f"Job: {job_id}. Option '{bad_option_name}' 's value '{bad_option_value}' "
            f"has an invalid type: {type(bad_option_value)}. "
            f"Valid type/s is/are: {expected_option_type}"
        )

        super().__init__(self.message)


class SplashScreenBadDimensionsError(Exception):
    """When splash screen image does not comply with recomended dimensions."""

    def __init__(self, image_filepath: Path, profile_name: str | None = None):
        """Initialization method.

        Args:
            image_filepath (Path): path to the selected image to be set as splash screen
            profile_name (str, optional): name of profile. Defaults to None.
        """
        self.message = (
            f"Profile {profile_name} -"
            f"{image_filepath.resolve()} dimensions "
            f"{get_image_size(image_filepath=image_filepath)} do not comply with "
            " dimensions recomended by QGIS for splash screen: 600x300."
        )
        super().__init__(self.message)


class QgisInstallNotFoundError(Exception):
    """When no QGIS installation are found."""

    def __init__(self):
        """Initialization method."""
        self.message = "No QGIS installation found."
        super().__init__(self.message)

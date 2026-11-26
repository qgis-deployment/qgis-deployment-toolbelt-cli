#! python3  # noqa: E265

"""Base model of the QDT jobs options, built on pydantic.

The options of a job are declared as a :class:`JobOptions` subclass, one annotated
field per option, and validated with :meth:`JobOptions.from_dict`:

- an option with a default value is optional, an option without one is required;
- unknown options are rejected;
- values are checked strictly: no conversion (``"5"`` is not accepted for an int);
- validated options are read-only.

Validation errors are raised as the QDT job options exceptions, to keep the same
messages and ``except`` clauses as the legacy ``OPTIONS_SCHEMA`` validation.

Example:
    .. code-block:: python

        class ExampleOptions(JobOptions):
            mode: Literal["fast", "safe"] = "safe"
            threads: int = 5
            source: str  # no default: required


        options = ExampleOptions.from_dict({"source": "here"}, job_id="example-job")
        options.mode  # "safe"

Author: Julien Moura (https://github.com/guts)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
from collections.abc import Mapping
from typing import Any, Literal, Self, get_args, get_origin

# 3rd party
from pydantic import BaseModel, ConfigDict, ValidationError
from pydantic_core import ErrorDetails

# package
from qgis_deployment_toolbelt.exceptions import (
    JobOptionBadNameError,
    JobOptionBadValueError,
    JobOptionBadValueTypeError,
    JobOptionMissingError,
)


# #############################################################################
# ########## Classes ###############
# ##################################


class JobOptions(BaseModel):
    """Base of the options of a job."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        validate_default=True,
    )

    @classmethod
    def from_dict(cls, options: Mapping[str, Any] | None, job_id: str) -> Self:
        """Validate the options set in the ``with`` key of a scenario step and
        complete them with the default values.

        Args:
            options: options to validate. None (step without ``with`` key) means that
                the default values apply and the required options are reported missing.
            job_id: job identifier, used in error messages

        Raises:
            TypeError: if options is neither a mapping nor None
            JobOptionBadNameError: if an option is not declared
            JobOptionMissingError: if a required option is not set
            JobOptionBadValueTypeError: if an option value has the wrong type
            JobOptionBadValueError: if an option value is not accepted

        Returns:
            validated options
        """
        if options is None:
            options = {}
        elif not isinstance(options, Mapping):
            raise TypeError(f"Options to validate must be a dict, not {type(options)}.")

        try:
            return cls.model_validate(options)
        except ValidationError as exc:
            # report the first error, like the legacy validation
            raise cls._to_qdt_error(exc.errors()[0], job_id=job_id) from exc

    @classmethod
    def _to_qdt_error(cls, error: ErrorDetails, job_id: str) -> Exception:
        """Translate a pydantic validation error into a QDT job option exception.

        Args:
            error: first error of the pydantic ValidationError
            job_id: job identifier, used in error messages

        Returns:
            exception to raise
        """
        option_name = ".".join(str(part) for part in error["loc"])
        # annotation of the option, when the error is on a top-level option
        field = cls.model_fields.get(option_name)
        annotation = field.annotation if field else None

        if error["type"] == "extra_forbidden":
            return JobOptionBadNameError(
                job_id=job_id,
                bad_option_name=option_name,
                expected_options_names=cls.model_fields.keys(),
            )
        if error["type"] == "missing":
            return JobOptionMissingError(job_id=job_id, missing_option_name=option_name)
        if error["type"] == "literal_error":
            accepted_values = (
                get_args(annotation)
                if get_origin(annotation) is Literal
                else (error.get("ctx", {}).get("expected", ""),)
            )
            return JobOptionBadValueError(
                job_id=job_id,
                bad_option_name=option_name,
                bad_option_value=error["input"],
                condition="in",
                accepted_values=[str(value) for value in accepted_values],
            )
        if error["type"].endswith("_type"):
            return JobOptionBadValueTypeError(
                job_id=job_id,
                bad_option_name=option_name,
                bad_option_value=error["input"],
                expected_option_type=annotation or error["msg"],
            )
        return JobOptionBadValueError(
            job_id=job_id,
            bad_option_name=option_name,
            bad_option_value=error["input"],
            condition=error["msg"],
        )

#! python3  # noqa: E265

"""Declarative options of QDT jobs.

Inspired by the Properdocs/MkDocs configuration options: each option is a descriptor
declared as a class attribute of a :class:`JobOptions` subclass. The option validates
the value set in the scenario (``with`` key of a step) and provides the default value
when it is not set.

An option without default value is required. ``None`` is a valid default value.

Example:
    .. code-block:: python

        class ExampleOptions(JobOptions):
            mode = Choice(("fast", "safe"), default="safe")
            threads = Type(int, default=5)
            source = Type(str)  # no default: required


        options = ExampleOptions.from_dict({"source": "here"}, job_id="example-job")
        options.mode  # "safe"

Author: Julien Moura (https://github.com/guts)

See: https://github.com/ProperDocs/properdocs/blob/master/properdocs/config/config_options.py
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
from collections.abc import Iterable, Mapping
from copy import deepcopy
from enum import Enum
from typing import Any, Final, Generic, Literal, NoReturn, Self, TypeVar, overload

# package
from qgis_deployment_toolbelt.exceptions import (
    JobOptionBadNameError,
    JobOptionBadValueError,
    JobOptionBadValueTypeError,
    JobOptionMissingError,
)


# #############################################################################
# ########## Types #################
# ##################################

T = TypeVar("T")


class _Missing(Enum):
    """Sentinel type for options without default value."""

    MISSING = "MISSING"


MISSING: Final = _Missing.MISSING

# #############################################################################
# ########## Classes ###############
# ##################################


class JobOption(Generic[T]):
    """Base of a job option.

    Subclasses override :meth:`validate`.

    Args:
        default: value used when the option is not set. Without default, the option is
            required. ``None`` is a valid default value.
    """

    def __init__(self, *, default: T | Literal[_Missing.MISSING] = MISSING) -> None:
        self.default = default
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        """Store the option name and check the default value against the option rules.

        Args:
            owner: options class declaring the option
            name: attribute name, i.e. option name in the scenario
        """
        self.name = name
        if self.default is not MISSING and self.default is not None:
            self.validate(self.default, job_id=owner.__name__)

    # typing only (no effect at runtime): tells type checkers and IDEs that the
    # attribute is the option on the class (``Options.mode``) and its value, of type
    # T, on an instance (``options.mode``). Same pattern as MkDocs config options.
    @overload
    def __get__(self, obj: None, objtype: type | None = None) -> Self: ...

    @overload
    def __get__(self, obj: "JobOptions", objtype: type | None = None) -> T: ...

    def __get__(self, obj: "JobOptions | None", objtype: type | None = None) -> Any:
        """Return the option itself on the class, the option value on an instance."""
        if obj is None:
            return self
        return obj._values[self.name]

    def __set__(self, obj: "JobOptions", value: Any) -> NoReturn:
        """Options are read-only once validated."""
        raise AttributeError(f"Option '{self.name}' is read-only.")

    @property
    def required(self) -> bool:
        """True when the option has no default value."""
        return self.default is MISSING

    def get_default(self) -> T:
        """Return a copy of the default value, to not share mutable values (lists...)
        between jobs.

        Returns:
            copy of the default value
        """
        if self.default is MISSING:
            raise ValueError(f"Option '{self.name}' has no default value.")
        return deepcopy(self.default)

    def validate(self, value: Any, job_id: str) -> T:
        """Check the value set in the scenario.

        Args:
            value: value to check
            job_id: job identifier, used in error messages

        Returns:
            the value, possibly converted
        """
        return value


class Type(JobOption[T]):
    """Option whose value must be an instance of the expected type(s).

    Args:
        expected_type: type or tuple of types accepted
        default: see :class:`JobOption`

    Raises:
        JobOptionBadValueTypeError: if the value is not of the expected type
    """

    def __init__(
        self,
        expected_type: type[T] | tuple[type, ...],
        *,
        default: T | Literal[_Missing.MISSING] = MISSING,
    ) -> None:
        self.expected_type = expected_type
        super().__init__(default=default)

    def validate(self, value: Any, job_id: str) -> T:
        """Check the value type. See :meth:`JobOption.validate`."""
        if not isinstance(value, self.expected_type):
            raise JobOptionBadValueTypeError(
                job_id=job_id,
                bad_option_name=self.name,
                bad_option_value=value,
                expected_option_type=self.expected_type,
            )
        return value


class Choice(JobOption[str]):
    """Option whose value must be one of a closed set of strings.

    Args:
        choices: accepted values
        default: see :class:`JobOption`

    Raises:
        JobOptionBadValueError: if the value is not one of the choices
    """

    def __init__(
        self,
        choices: Iterable[str],
        *,
        default: str | None | Literal[_Missing.MISSING] = MISSING,
    ) -> None:
        self.choices: tuple[str, ...] = tuple(choices)
        super().__init__(default=default)

    def validate(self, value: Any, job_id: str) -> str:
        """Check the value is one of the choices. See :meth:`JobOption.validate`."""
        if value not in self.choices:
            raise JobOptionBadValueError(
                job_id=job_id,
                bad_option_name=self.name,
                bad_option_value=value,
                condition="in",
                accepted_values=self.choices,
            )
        return value


class JobOptions:
    """Base of the options of a job, declared as :class:`JobOption` class attributes.

    Build instances with :meth:`from_dict`, which validates the options and completes
    them with the default values.
    """

    def __init__(self, values: dict[str, Any]) -> None:
        """Store already validated values. Use :meth:`from_dict` instead.

        Args:
            values: validated values, by option name
        """
        self._values: dict[str, Any] = values

    def __repr__(self) -> str:
        """Return a representation listing the options values."""
        values = ", ".join(f"{name}={value!r}" for name, value in self._values.items())
        return f"{type(self).__name__}({values})"

    @classmethod
    def declared_options(cls) -> dict[str, JobOption[Any]]:
        """Return the options declared on the class and its parents.

        Returns:
            options by name, in declaration order
        """
        options: dict[str, JobOption[Any]] = {}
        for klass in reversed(cls.__mro__):
            for name, attr in vars(klass).items():
                if isinstance(attr, JobOption):
                    options[name] = attr
        return options

    @classmethod
    def from_dict(cls, options: Mapping[str, Any], job_id: str) -> Self:
        """Validate the options set in the scenario and complete them with the default
        values.

        Args:
            options: options set in the ``with`` key of a scenario step
            job_id: job identifier, used in error messages

        Raises:
            TypeError: if options is not a mapping
            JobOptionBadNameError: if an option is not declared
            JobOptionMissingError: if a required option is not set
            JobOptionBadValueError: if an option value fails its condition
            JobOptionBadValueTypeError: if an option value has the wrong type

        Returns:
            validated options
        """
        if not isinstance(options, Mapping):
            raise TypeError(f"Options to validate must be a dict, not {type(options)}.")

        declared = cls.declared_options()
        for name in options:
            if name not in declared:
                raise JobOptionBadNameError(
                    job_id=job_id,
                    bad_option_name=name,
                    expected_options_names=declared.keys(),
                )

        values: dict[str, Any] = {}
        for name, option in declared.items():
            if name in options:
                values[name] = option.validate(options[name], job_id=job_id)
            elif option.required:
                raise JobOptionMissingError(job_id=job_id, missing_option_name=name)
            else:
                values[name] = option.get_default()

        return cls(values)

    def as_dict(self) -> dict[str, Any]:
        """Return a copy of the options values, e.g. for logging.

        Returns:
            options values by name
        """
        return deepcopy(self._values)

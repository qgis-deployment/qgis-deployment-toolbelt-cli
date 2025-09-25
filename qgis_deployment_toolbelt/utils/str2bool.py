#! python3  # noqa: E265

"""
Basic string to bool.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging


# #############################################################################
# ########## Globals ###############
# ##################################

_true_set = {"on", "t", "true", "y", "yes", "1"}
_false_set = {"f", "false", "n", "no", "off", "0"}
logger = logging.getLogger(__name__)

# #############################################################################
# ########## Functions #############
# ##################################


def str2bool(input_var: bool | str, raise_exc: bool = False) -> bool | None:
    """Determine if a string is a bool and, if so, convert it.

    Args:
        input_var (str): value to convert
        raise_exc (bool, optional): strict mode, defaults to False.

    Raises:
        ValueError: input_var is not in true and false sets
        TypeError: if input_var is not a str or a bool

    Returns:
        bool: True if input_var is in _true_set, False if it's in _false_set.
    None or Exception if not in any of two sets.
    """
    if isinstance(input_var, str):
        value = input_var.lower()
        if value in _true_set:
            return True
        if value in _false_set:
            return False

        error_message = 'Expected "%s"' % '", "'.join(_true_set | _false_set)
        if raise_exc:
            raise ValueError(error_message)
        else:
            logger.error(error_message)
            return None
    elif isinstance(input_var, bool):
        logger.debug(f"Value {input_var} was already a bool.")
        return input_var
    else:
        error_message = f"Value must be a str, not {type(input_var)}"
        if raise_exc:
            raise TypeError(error_message)
        else:
            logger.error(error_message)
            return None

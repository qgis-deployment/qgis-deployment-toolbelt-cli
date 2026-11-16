#! python3  # noqa: E265

"""Guard the isolation of the test session set up in ``tests/conftest.py``.

Usage from the repo root folder:

.. code-block:: bash

    pytest tests/test_tests_isolation.py
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import os
import sys
import tempfile
from pathlib import Path

# 3rd party
import pytest

# package
from qgis_deployment_toolbelt.constants import DEFAULT_QDT_WORKING_FOLDER
from qgis_deployment_toolbelt.utils import os_linux


# #############################################################################
# ########## Tests #################
# ##################################

skip_on_windows = pytest.mark.skipif(
    sys.platform == "win32", reason="user folders are not redirected on Windows"
)


@skip_on_windows
def test_home_is_isolated():
    """The user folder, and the paths computed from it at import, are temporary."""
    temp_root = Path(tempfile.gettempdir()).resolve()

    assert Path.home().resolve().is_relative_to(temp_root)
    assert DEFAULT_QDT_WORKING_FOLDER.resolve().is_relative_to(temp_root)
    assert os_linux.bash_user_dot_profile.resolve().is_relative_to(temp_root)


def test_environment_change_part_1():
    """Set and remove variables: the next test must not see the changes."""
    os.environ["QDT_TEST_ISOLATION_LEAK"] = "leaked"
    os.environ.pop("HOME", None)


def test_environment_change_part_2():
    """Variables changed by the previous test are restored."""
    assert "QDT_TEST_ISOLATION_LEAK" not in os.environ
    if sys.platform != "win32":
        assert "HOME" in os.environ

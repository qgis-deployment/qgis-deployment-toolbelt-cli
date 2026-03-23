#! python3  # noqa: E265

"""
Test CLI's main command.

Author: Julien Moura (Oslandia)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import tempfile
from os import environ
from pathlib import Path

# 3rd party
# project
from qgis_deployment_toolbelt.utils.journalizer import configure_logger


def test_configure_logger_logfile():
    with tempfile.TemporaryDirectory(
        prefix="QDT_test_journalizer_logfile",
        ignore_cleanup_errors=True,
    ) as tmpdirname:
        environ["QDT_LOGS_DELAY_FILE_CREATION"] = "False"
        configure_logger(verbosity=4, logfile="test.log", logs_folder=Path(tmpdirname))
        assert Path(Path(tmpdirname) / "test.log").exists()

    # clean up environment vars
    environ.pop("QDT_LOGS_DELAY_FILE_CREATION")


def test_configure_logger_default_log_dir():
    with tempfile.TemporaryDirectory(
        prefix="QDT_test_journalizer_default_log_dir",
        ignore_cleanup_errors=True,
    ) as tmpdirname:
        qdt_working_folder = Path(tmpdirname).joinpath("qdt_working_folder")
        environ["QDT_LOCAL_WORK_DIR"] = f"{qdt_working_folder.resolve()}"

        environ["QDT_LOGS_DELAY_FILE_CREATION"] = "False"
        configure_logger(verbosity=4, logfile="test.log")
        assert Path(Path(qdt_working_folder) / "logs" / "test.log").exists()

    # clean up environment vars
    environ.pop("QDT_LOGS_DELAY_FILE_CREATION")
    environ.pop("QDT_LOCAL_WORK_DIR")

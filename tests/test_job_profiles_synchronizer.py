#! python3  # noqa E265

"""Test the profiles synchronizer job.

Usage from the repo root folder:

.. code-block:: bash

    pytest tests/test_job_profiles_synchronizer.py
"""

# standard
import json
import shutil
from configparser import ConfigParser
from datetime import datetime
from pathlib import Path

# 3rd party
import pytest

# project
from qgis_deployment_toolbelt.__about__ import __version_clean__
from qgis_deployment_toolbelt.exceptions import JobOptionBadValueError
from qgis_deployment_toolbelt.jobs.job_profiles_synchronizer import (
    JobProfilesSynchronizer,
)
from qgis_deployment_toolbelt.profiles.qdt_profile import QdtProfile


# ############################################################################
# ########## Helpers #############
# ################################


def _make_downloaded_profile(
    parent_folder: Path, profile_json: dict, qgis_ini: str | None
) -> QdtProfile:
    """Create a downloaded profile folder and return the matching QdtProfile.

    Args:
        parent_folder: folder where to create the profile folder
        profile_json: content of the profile.json file
        qgis_ini: content of the QGIS/QGIS3.ini file, None to not create it

    Returns:
        QdtProfile: profile loaded from the created profile.json
    """
    profile_folder = parent_folder / profile_json["name"]
    profile_folder.mkdir(parents=True)
    profile_folder.joinpath("profile.json").write_text(
        json.dumps(profile_json), encoding="UTF-8"
    )
    if qgis_ini is not None:
        profile_folder.joinpath("QGIS").mkdir()
        profile_folder.joinpath("QGIS", "QGIS3.ini").write_text(
            qgis_ini, encoding="UTF-8"
        )
    return QdtProfile.from_json(
        profile_json_path=profile_folder / "profile.json",
        profile_folder=profile_folder,
    )


def _read_installed_ini(profile: QdtProfile) -> ConfigParser:
    """Read the settings file of the installed profile.

    Args:
        profile: downloaded profile

    Returns:
        ConfigParser: parsed settings file of the installed profile
    """
    cfg_parser = ConfigParser(interpolation=None)
    cfg_parser.optionxform = str
    cfg_parser.read(profile.path_in_qgis / "QGIS" / profile.qgis_ini_filename)
    return cfg_parser


@pytest.fixture
def profile_json() -> dict:
    """profile.json content with a profile name unique to the test session."""
    return {
        "name": f"qdt_test_watermark_{datetime.now():%Y%m%d%H%M%S%f}",
        "version": "1.2.0",
        "author": "GIS team",
        "email": "gis-team@example.org",
    }


@pytest.fixture
def cleanup_installed_profile(profile_json: dict):
    """Remove the installed profile folder after the test."""
    yield
    installed = QdtProfile(name=profile_json["name"]).path_in_qgis
    shutil.rmtree(installed, ignore_errors=True)


# ############################################################################
# ########## Tests ###############
# ################################


def test_qdt_watermark_bad_value():
    """An unknown qdt_watermark value is rejected."""
    with pytest.raises(JobOptionBadValueError):
        JobProfilesSynchronizer(options={"qdt_watermark": "everywhere"})


@pytest.mark.usefixtures("cleanup_installed_profile")
@pytest.mark.parametrize(
    ("qdt_watermark", "expected_section"),
    [("section", "QDT"), ("variables", "variables")],
)
def test_qdt_watermark_written_after_merge(
    tmp_path: Path, profile_json: dict, qdt_watermark: str, expected_section: str
):
    """Metadata are written in the expected section, never in backup sections."""
    downloaded = _make_downloaded_profile(
        parent_folder=tmp_path,
        profile_json=profile_json,
        qgis_ini="[variables]\nenv=production\n",
    )
    job = JobProfilesSynchronizer(options={"qdt_watermark": qdt_watermark})

    # install then update: the second sync merges into an already watermarked file
    job.sync_overwrite_local_profiles(profiles_to_copy=[downloaded])
    job.sync_overwrite_local_profiles(profiles_to_copy=[downloaded])

    cfg_parser = _read_installed_ini(downloaded)
    watermark = cfg_parser[expected_section]
    assert watermark["qdt_profile_version"] == "1.2.0"
    assert watermark["qdt_profile_author"] == "GIS team"
    assert watermark["qdt_profile_email"] == "gis-team@example.org"
    assert watermark["qdt_version"] == __version_clean__
    assert datetime.fromisoformat(watermark["qdt_profile_last_sync"]).tzinfo
    # settings shipped by the profile are still there
    assert cfg_parser["variables"]["env"] == "production"
    # watermark never ends up in backup sections
    for section in cfg_parser.sections():
        if section.startswith("QDT_backup_"):
            assert not any(key.startswith("qdt_") for key in cfg_parser[section])


@pytest.mark.usefixtures("cleanup_installed_profile")
def test_qdt_watermark_creates_missing_settings_file(
    tmp_path: Path, profile_json: dict
):
    """The settings file is created when the profile doesn't ship one."""
    del profile_json["email"]
    downloaded = _make_downloaded_profile(
        parent_folder=tmp_path, profile_json=profile_json, qgis_ini=None
    )
    job = JobProfilesSynchronizer(options={"qdt_watermark": "section"})

    job.sync_overwrite_local_profiles(profiles_to_copy=[downloaded])

    cfg_parser = _read_installed_ini(downloaded)
    assert cfg_parser["QDT"]["qdt_profile_version"] == "1.2.0"
    assert "qdt_profile_email" not in cfg_parser["QDT"]


@pytest.mark.usefixtures("cleanup_installed_profile")
def test_qdt_watermark_none_by_default(tmp_path: Path, profile_json: dict):
    """Nothing is written when the option is not set."""
    downloaded = _make_downloaded_profile(
        parent_folder=tmp_path,
        profile_json=profile_json,
        qgis_ini="[variables]\nenv=production\n",
    )
    job = JobProfilesSynchronizer(options={})

    job.sync_overwrite_local_profiles(profiles_to_copy=[downloaded])

    cfg_parser = _read_installed_ini(downloaded)
    assert "QDT" not in cfg_parser
    assert not any(key.startswith("qdt_") for key in cfg_parser["variables"])

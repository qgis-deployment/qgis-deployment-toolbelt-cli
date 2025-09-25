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
from os import environ, getenv
from pathlib import Path

# 3rd party
import pytest

# project
from qgis_deployment_toolbelt import __about__, cli
from qgis_deployment_toolbelt.profiles.qdt_profile import QdtProfile


# #############################################################################
# ######## Globals #################
# ##################################

sample_scenario_good: Path = Path(
    "tests/fixtures/scenarios/good_scenario_sample.qdt.yml"
)
sample_scenario_good_with_unexisting_jobs: Path = Path(
    "tests/fixtures/scenarios/good_scenario_with_unexisting_jobs.qdt.yml"
)
sample_scenario_good_splash_removal: Path = Path(
    "tests/fixtures/scenarios/good_scenario_splash_screen_remove.qdt.yml"
)

sample_scenario_false: Path = Path(
    "tests/fixtures/scenarios/false_scenario_sample.qdt.yml"
)
sample_scenario_imaginary: Path = Path(
    "tests/fixtures/scenarios/imaginary_scenario_sample.qdt.yml"
)

good_scenarios = [
    ["deploy", f"--scenario={scenario_path.resolve()}"]
    for scenario_path in Path("tests/fixtures/scenarios/").glob("good_*.qdt.yml")
]

# #############################################################################
# ######## Classes #################
# ##################################


@pytest.mark.parametrize("option", ("-h", "--help"))
def test_cli_help(capsys, option):
    """Test CLI help."""
    with pytest.raises(SystemExit):
        cli.main([option])

    out, err = capsys.readouterr()

    assert (
        f"{__about__.__title__} {__about__.__version__} - {__about__.__summary__}"
        in out
    )
    assert err == ""


@pytest.mark.parametrize("option", (["--version"]))
def test_cli_version(capsys, option):
    """Test CLI version."""
    with pytest.raises(SystemExit):
        cli.main([option])

    out, err = capsys.readouterr()

    assert f"{__about__.__version__}\n" == out

    assert err == ""


@pytest.mark.parametrize("option", good_scenarios)
def test_main_run(capsys, option):
    """Test main cli command"""

    with tempfile.TemporaryDirectory(
        prefix="QDT_test_cli_run_",
        ignore_cleanup_errors=True,
    ) as tmpdirname:
        # customize QDT working folder and profiles destination folder
        tmp_dir = Path(tmpdirname).joinpath(f"scenario_{good_scenarios.index(option)}")
        environ["QDT_LOCAL_WORK_DIR"] = (
            f"{Path(tmpdirname).joinpath('qdt_working_folder').resolve()}"
        )
        environ["QGIS_CUSTOM_CONFIG_PATH"] = f"{tmp_dir.resolve()}"

        assert getenv("QGIS_CUSTOM_CONFIG_PATH") is not None

        with pytest.raises(SystemExit):
            cli.main(option)

        _, err = capsys.readouterr()
        assert err == ""

        # checks
        created_profiles = [
            QdtProfile.from_json(profile_json_path=f, profile_folder=f.parent)
            for f in tmp_dir.glob("**/profile.json")
        ]

        assert Path(getenv("QGIS_CUSTOM_CONFIG_PATH")).is_dir()
        assert len(created_profiles) > 0

    # clean up environment vars
    environ.pop("QGIS_CUSTOM_CONFIG_PATH")


def test_main_run_as_admin(capsys):
    """Test main cli command on scenario requiring admin rights"""
    with pytest.raises(SystemExit):
        cli.main(
            [
                "deploy",
                f"--scenario={Path('tests/fixtures/scenarios/scenario_sample_as_admin.qdt.yml').resolve()}",
            ]
        )

    _, err = capsys.readouterr()
    assert err == ""


def test_main_run_unexising_jobs(capsys):
    """Test main cli command"""
    with pytest.raises(SystemExit):
        cli.main(
            [
                "deploy",
                f"--scenario={str(sample_scenario_good_with_unexisting_jobs.resolve())}",
            ]
        )

    _, err = capsys.readouterr()
    assert err == ""


def test_main_run_failed(capsys):
    """Test main cli command"""
    with pytest.raises(FileExistsError):
        cli.main(["deploy", f"--scenario={str(sample_scenario_false.resolve())}"])

    _, err = capsys.readouterr()
    assert err == ""


def test_main_run_removing_splash(capsys):
    """Test main cli command"""
    with tempfile.TemporaryDirectory(
        prefix="qdt_test_cli_main_", ignore_cleanup_errors=True
    ) as tmpdirname:
        environ["QGIS_CUSTOM_CONFIG_PATH"] = tmpdirname
        with pytest.raises(SystemExit):
            cli.main(
                [
                    "deploy",
                    f"--scenario={sample_scenario_good_splash_removal.resolve()}",
                ]
            )

        _, err = capsys.readouterr()
        assert err == ""

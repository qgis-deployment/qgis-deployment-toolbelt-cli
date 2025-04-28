#! python3  # noqa: E265

"""Setup script to package into a Python module."""

# ############################################################################
# ########## Libraries #############
# ##################################

# standard library
from pathlib import Path

# 3rd party
from setuptools import find_packages, setup

# package (to get version)
from qgis_deployment_toolbelt import __about__

# ############################################################################
# ########### Globals ##############
# ##################################

# The directory containing this file
HERE = Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text(encoding="UTF-8")

# ############################################################################
# ########### Functions ############
# ##################################


def load_requirements(requirements_files: Path | list[Path]) -> list:
    """Helper to load requirements list from a path or a list of paths.

    Args:
        requirements_files (Path | list[Path]): path or list to paths of requirements
            file(s)

    Returns:
        list: list of requirements loaded from file(s)
    """
    out_requirements = []

    if isinstance(requirements_files, Path):
        requirements_files = [
            requirements_files,
        ]

    for requirements_file in requirements_files:
        with requirements_file.open(encoding="UTF-8") as f:
            out_requirements += [
                line
                for line in f.read().splitlines()
                if not line.startswith(("#", "-")) and len(line)
            ]

    return out_requirements


# ############################################################################
# ########### Main #################
# ##################################

setup(
    name=__about__.__package_name__,
    author=__about__.__author__,
    author_email=__about__.__email__,
    description=__about__.__summary__,
    long_description=README,
    long_description_content_type="text/markdown",
    keywords=__about__.__keywords__,
    url=__about__.__uri__,
    version=__about__.__version__,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: System :: Installation/Setup",
    ],
    # packaging
    python_requires=">=3.10,<4",
    py_modules=["qgis_deployment_toolbelt"],
    packages=find_packages(
        exclude=["contrib", "docs", "*.tests", "*.tests.*", "tests.*", "tests", ".venv"]
    ),
    include_package_data=True,
    install_requires=load_requirements(HERE / "requirements/base.txt"),
    extras_require={
        # tooling
        "dev": load_requirements(HERE / "requirements/development.txt"),
        "doc": load_requirements(HERE / "requirements/documentation.txt"),
        "test": load_requirements(HERE / "requirements/testing.txt"),
    },
    entry_points={
        "console_scripts": [
            f"{__about__.__executable_name__}=qgis_deployment_toolbelt.cli:main",
            "qdeploy-toolbelt=qgis_deployment_toolbelt.cli:main",
            "qdt=qgis_deployment_toolbelt.cli:main",
        ]
    },
)

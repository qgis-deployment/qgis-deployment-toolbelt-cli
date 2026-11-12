#! python3  # noqa: E265

"""Manifest of the shortcuts created by QDT."""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

# project
from qgis_deployment_toolbelt.__about__ import __version_clean__
from qgis_deployment_toolbelt.constants import ShortcutLocation


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Functions ###############
# ##################################


def _add_shortcut_to_manifest(
    manifest: dict[str, dict[str, str]],
    shortcut_path: Path,
    profile_folder: Path,
    location: ShortcutLocation,
) -> None:
    """Add/update a shortcut to the QDT shortcuts manifest.

    Args:
        manifest (dict[str, dict[str, str]]): manifest dict to amend, in place
        shortcut_path (Path): path to the plugin that has just been installed
        profile_folder (Path): path to the profile folder targeted by the shortcut
        location (ShortcutLocation): where the shortcut has been created
    """
    # paths are case-insensitive on Windows so replace an equivalent entry
    for existing_path in [k for k in manifest if Path(k) == shortcut_path]:
        del manifest[existing_path]

    manifest[str(shortcut_path)] = {
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
        "location": location,
        "profile_folder": str(profile_folder),
        "qdt_version": f"{__version_clean__}",
    }


def _read_qdt_managed_shortcuts_manifest(
    manifest_path: Path,
) -> dict[str, dict[str, str]]:
    """Read the QDT managed plugins manifest from disk, if it exists.

    Args:
        manifest_path (Path): path to the manifest file

    Returns:
        dict[str, dict[str, str]]: manifest content, or an empty dict if the
        file doesn't exist or is corrupted
    """
    if not manifest_path.is_file():
        return {}

    try:
        return json.loads(manifest_path.read_text(encoding="UTF-8"))
    except json.JSONDecodeError as err:
        logger.warning(
            f"QDT managed shortcuts manifest '{manifest_path}' is corrupted, it "
            f"will be recreated. Trace: {err}"
        )
        return {}


def _write_qdt_managed_shortcuts_manifest(
    manifest_path: Path, manifest: dict[str, dict[str, str]]
) -> None:
    """Write the QDT managed plugins manifest to file.

    Args:
        manifest_path (Path): path to the manifest file
        manifest (dict[str, dict[str, str]]): manifest content to write
    """
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="UTF-8"
    )
    logger.debug(f"QDT managed shortcuts manifest written: {manifest_path}")

#! python3  # noqa: E265

"""
Synchronize plugins between downloaded and installed profiles.

Author: Julien Moura (https://github.com/guts)
"""


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
from qgis_deployment_toolbelt.plugins.plugin import QgisPlugin


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Functions ###############
# ##################################


def _add_plugin_to_manifest(
    manifest: dict[str, dict[str, str]], plugin: QgisPlugin
) -> None:
    """Add/update a plugin to the QDT profile manifest.

    Args:
        manifest (dict[str, dict[str, str]]): manifest dict to amend, in place
        plugin (QgisPlugin): plugin that has just been installed
    """
    manifest[plugin.installation_folder_name] = {
        "installed_at": datetime.now(tz=timezone.utc).isoformat(),
        "plg_id": f"{plugin.plugin_id}",
        "plg_version": plugin.version,
        "qdt_version": f"{__version_clean__}",
    }


def _read_qdt_managed_plugins_manifest(
    manifest_path: Path,
) -> dict[str, dict[str, str]]:
    """Read the QDT-managed plugins manifest from disk, if it exists.

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
            f"QDT managed plugins manifest '{manifest_path}' is corrupted, it "
            f"will be recreated. Trace: {err}"
        )
        return {}


def _write_qdt_managed_plugins_manifest(
    manifest_path: Path, manifest: dict[str, dict[str, str]]
) -> None:
    """Write the QDT-managed plugins manifest to file.

    Args:
        manifest_path (Path): path to the manifest file
        manifest (dict[str, dict[str, str]]): manifest content to write
    """
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="UTF-8"
    )
    logger.debug(f"QDT managed plugins manifest written: {manifest_path}")

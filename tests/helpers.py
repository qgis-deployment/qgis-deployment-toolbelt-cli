#! python3  # noqa: E265

"""Helpers shared by tests."""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import io
import zipfile


# #############################################################################
# ########## Functions #############
# ##################################


def build_fake_plugin_zip(
    folder_name: str, version: str, name: str | None = None
) -> bytes:
    """Build in memory a minimal QGIS plugin ZIP archive.

    Args:
        folder_name: name of the plugin folder at the root of the archive
        version: plugin version
        name: plugin name written in metadata.txt. Defaults to the folder name.

    Returns:
        ZIP archive content
    """
    metadata = (
        "[general]\n"
        f"name={name or folder_name}\n"
        f"version={version}\n"
        "qgisMinimumVersion=3.16\n"
        "qgisMaximumVersion=4.99\n"
        "description=Fake plugin used by QDT tests.\n"
        "author=QDT tests\n"
        "email=qdt@example.org\n"
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as zf:
        zf.writestr(f"{folder_name}/metadata.txt", metadata)
        zf.writestr(f"{folder_name}/__init__.py", "")
    return buffer.getvalue()

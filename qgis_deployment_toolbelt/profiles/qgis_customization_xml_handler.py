#! python3  # noqa: E265

"""Read and write the QGIS UI customization file (QGISCUSTOMIZATION.xml), replacement of
QGISCUSTOMIZATION3.ini since QGIS 4.

See: https://github.com/qgis/QGIS/blob/master/src/app/qgscustomization.cpp
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
import xml.etree.ElementTree as ET
from pathlib import Path

# package
from qgis_deployment_toolbelt.exceptions import QgisCustomizationXmlError


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################


class QgisCustomizationXmlHelper:
    """Helper to manipulate the QGIS  4+ UI customization file (QGISCUSTOMIZATION.xml)."""

    # QGIS fromat version
    # see: https://github.com/qgis/QGIS/blob/final-4_2_3/src/app/qgscustomization.cpp#L1833
    FORMAT_VERSION: str = "1"

    # top-level items written by QGIS. A missing one is read as not visible.
    ROOT_ITEMS: tuple[str, ...] = (
        "BrowserItems",
        "Docks",
        "Menus",
        "StatusBarWidgets",
        "ToolBars",
    )

    def __init__(self, xml_filepath: Path) -> None:
        """Instanciation.

        Args:
            xml_filepath (Path): path to the QGISCUSTOMIZATION.xml file. It may not
                exist.
        """
        self.xml_filepath = xml_filepath

    def read(self) -> ET.Element | None:
        """Parse the customization file.

        Raises:
            QgisCustomizationXmlError: if the file can't be parsed or is not a QGIS
                customization file.

        Returns:
            ET.Element | None: root element or None if the file does not exist.
        """
        if not self.xml_filepath.exists():
            return None

        try:
            # Security flags: the underlying XML parser expat mitigates security issues
            # since its version 2.4.1 which is embedded in CPython >= 3.11.
            # see: https://docs.python.org/3/library/xml.html#xml-vulnerabilities
            root = ET.parse(self.xml_filepath).getroot()  # noqa: B314 S314
        except (OSError, ET.ParseError) as err:
            raise QgisCustomizationXmlError(
                self.xml_filepath, f"Unable to parse the file. Trace: {err}"
            ) from err

        if root.tag != "Customization":
            raise QgisCustomizationXmlError(
                self.xml_filepath, f"root tag '{root.tag}' is not 'Customization'."
            )
        return root

    def write(self, root: ET.Element) -> None:
        """Write the customization file, formatted as QGIS does.

        Args:
            root (ET.Element): root element to write.
        """
        ET.indent(root, space="  ")
        self.xml_filepath.parent.mkdir(parents=True, exist_ok=True)
        with self.xml_filepath.open("w", encoding="UTF8") as xml_file:
            xml_file.write("<!DOCTYPE Customization>\n")
            xml_file.write(ET.tostring(root, encoding="unicode"))

    def is_splash_screen_set(self) -> bool:
        """Determine if a custom splash screen is set and enabled.

        Returns:
            bool: True if a splash screen path is set and the customization enabled.
        """
        try:
            root = self.read()
        except QgisCustomizationXmlError as err:
            logger.warning(err.message)
            return False

        return (
            root is not None
            and root.get("enabled") == "true"
            and bool(root.get("splashPath", "").strip())
        )

    def set_splash_screen(
        self, splash_screen_filepath: Path | None = None, switch: bool = True
    ) -> bool:
        """Add/remove the splash screen path in the customization file.

        Adding it also enables the customization, otherwise QGIS ignores it.

        Args:
            splash_screen_filepath (Path | None, optional): path to the splash screen
                image. Required if switch is True. Defaults to None.
            switch (bool, optional): True to add, False to remove. Defaults to True.

        Raises:
            ValueError: if switch is True but splash_screen_filepath is not defined.

        Returns:
            bool: True if the file is in the expected state.
        """
        if switch and splash_screen_filepath is None:
            raise ValueError(f"{switch=} but splash screen filepath is not defined.")

        try:
            root = self.read()
        except QgisCustomizationXmlError as err:
            logger.error(f"{err.message} File left untouched.")
            return False

        if not switch:
            if root is None or "splashPath" not in root.attrib:
                logger.debug(f"No splash screen to remove from {self.xml_filepath}")
                return True
            del root.attrib["splashPath"]
            self.write(root)
            logger.debug(f"Splash screen DISABLED in {self.xml_filepath}")
            return True

        # QGIS appends 'splash.png' to this path without separator
        splash_folder = f"{splash_screen_filepath.parent.resolve().as_posix()}/"

        if root is None:
            root = ET.Element("Customization", version=self.FORMAT_VERSION)
            for item in self.ROOT_ITEMS:
                ET.SubElement(root, item, name=item, visible="true")
        elif root.get("enabled") == "true" and root.get("splashPath") == splash_folder:
            logger.debug(f"Splash screen is already ENABLED in {self.xml_filepath}")
            return True

        root.set("enabled", "true")
        root.set("splashPath", splash_folder)
        self.write(root)
        logger.debug(f"Splash screen ENABLED in {self.xml_filepath}")
        return True

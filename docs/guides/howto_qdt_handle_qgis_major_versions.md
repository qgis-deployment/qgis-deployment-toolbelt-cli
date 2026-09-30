---
tags:
  - migration
  - QGIS
---

# How QDT support different QGIS major versions (QGIS 4 support)

Since its version 0.46, QDT works on machines where QGIS 4 is installed, alongside QGIS 3 or not.

## What changes between QGIS 3 and QGIS 4

QGIS stores the user's settings in folders and files named after its own **major version**. QDT follows the same rule:

| Item | QGIS 3 | QGIS 4 |
| :--- | :--- | :--- |
| Profiles folder (Windows) | `%APPDATA%\QGIS\QGIS3\profiles` | `%APPDATA%\QGIS\QGIS4\profiles` |
| Profiles folder (Linux) | `~/.local/share/QGIS/QGIS3/profiles` | `~/.local/share/QGIS/QGIS4/profiles` |
| Profiles folder (macOS) | `~/Library/Application Support/QGIS/QGIS3/profiles` | `~/Library/Application Support/QGIS/QGIS4/profiles` |
| Profile settings file | `<profile>/QGIS/QGIS3.ini` | `<profile>/QGIS/QGIS4.ini` |
| Profile customization file | `<profile>/QGIS/QGISCUSTOMIZATION3.ini` | `<profile>/QGIS/QGISCUSTOMIZATION.xml` |

In your IT follows the good practices on Windows, different QGIS versions should be deployed side by side under a common folder, by passing a custom `INSTALLDIR` to the MSI: `%PROGRAMFILES%\QGIS\3_44` or `%PROGRAMFILES%\QGIS\4_02` for example, instead of the installer's default `%PROGRAMFILES%\QGIS 3.34.15`. The [QGIS installation finder job](../jobs/qgis_installation_finder.md) searches the default locations of the MSI and OSGeo4W installers only, so declare such a custom location through its `search_paths` option:

```yaml
- name: Find installed QGIS
  uses: qgis-installation-finder
  with:
    search_paths:
      - "%PROGRAMFILES%/QGIS"
```

## How QDT picks the QGIS major version

1. The [`qgis-installation-finder`](../jobs/qgis_installation_finder.md) job locates the installed QGIS and exports its version as the `QDT_QGIS_VERSION` environment variable.
2. Every subsequent job derives the profiles folder and the settings filename from the major version of `QDT_QGIS_VERSION`.

> [!IMPORTANT]
> Put the `qgis-installation-finder` job **first** in your scenario. Without it, QDT has no way to know which QGIS is installed and falls back to QGIS 3.

The `QGIS_CUSTOM_CONFIG_PATH` environment variable still takes precedence over everything: when it is set, QDT uses it as the profiles folder whatever the QGIS major version, exactly like QGIS does.

## Targeting a specific QGIS version

When QGIS 3 and QGIS 4 are installed side by side, the most recent one wins by default. Pin the one your deployment targets with the `version_priority` option:

```yaml
- name: Find installed QGIS
  uses: qgis-installation-finder
  with:
    version_priority:
      - "3.40"
    if_not_found: error
```

Or, without editing the scenario, with the `QDT_PREFERRED_QGIS_VERSION` environment variable.

## Migrating profiles authored for QGIS 3

A profile shipping a `QGIS/QGIS3.ini` file deployed on a machine running QGIS 4 keeps working: QDT renames the file to `QGIS/QGIS4.ini` when installing the profile, so the settings it carries are not silently ignored by QGIS 4.

If a profile ships both files, both are copied as they are and QDT does not rename anything.

> [!NOTE]
> QGIS 3 and QGIS 4 profiles live in two distinct folders, so deploying to QGIS 4 does not modify the QGIS 3 profiles already installed on the machine.

## UI customization

> [!WARNING]
> **UI customization is only partially supported on QGIS 4**  
> Since the ini --> XML conversion is unexposed in the API and undocumented, QDT handles the splash screen in the QGIS 4 format only. Other customizations shipped in `QGISCUSTOMIZATION3.ini` (menus, toolbars...) still rely on the legacy import described below.

#### Splash screen

QGIS 4 stores the UI customization in `QGIS/QGISCUSTOMIZATION.xml` and reads the splash screen from its `splashPath` attribute, only if its `enabled` attribute is `true`. It imports `QGIS/QGISCUSTOMIZATION3.ini` only once, as a legacy import, while the XML file does not exist (see [related code in QGIS](https://github.com/qgis/QGIS/blob/final-4_2_3/src/app/qgscustomization.cpp)).

So, for a profile installed for QGIS 4, the [`splash-screen-manager`](../jobs/splash_screen_manager.md) job:

- updates `QGISCUSTOMIZATION.xml` if it exists, preserving the items customized with QGIS, and enables the customization;
- creates it if it does not exist, unless `QGISCUSTOMIZATION3.ini` holds other customizations than the splash screen (menus, toolbars...): the splash screen is then set in the ini file, to let QGIS import all of them at once;
- with `action: remove`, removes the splash screen from both files, leaving the customization state unchanged.

A `QGISCUSTOMIZATION.xml` file which is malformed or whose root tag is not `Customization` is left untouched and an error is logged.

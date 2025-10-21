# QGIS installation finder

Use this job to find installed QGIS version for automatic definition of QDT environnement variable `QDT_QGIS_EXE_PATH` (used for shortcut creation).

In certains conditions, the job is skipped:

- if the environment variable `QDT_QGIS_EXE_PATH` is already defined (either a simple string or a stringified dictionary);
- if the value points to an existing file.

Typically, if the scenario contains:

```yaml
settings:
  QGIS_EXE_PATH:
    linux: /usr/local/bin/qgis
    mac: /usr/bin/qgis
    windows: "%PROGRAMFILES%/QGIS/3_40/bin/qgis-ltr-bin.exe"
```

or

```yaml
settings:
  QGIS_EXE_PATH: "%PROGRAMFILES%/QGIS/3_40/bin/qgis-ltr-bin.exe"
```

And if paths are pointing to an existing file, the job is skipped.

----

## Compatibility

This job is compatible with:

- Windows
- Linux

----

## Use it

Sample job configuration in your scenario file:

```yaml
- name: Find installed QGIS
  uses: qgis-installation-finder
  with:
    version_priority:
      - "3.36"
    search_paths:
      - D:\\Applications\\QGIS\\
    if_not_found: error
```

----

## Options

### version_priority

Since multiple versions of QGIS can be easily installed on Windows, this option is used to specify the preferred QGIS version.

For example if you define:

```yaml
- name: Find installed QGIS
  uses: qgis-installation-finder
  with:
    - version_priority:
      - "3.34"
      - "3.36"
```

QDT will first use 3.34.z versions. If none are available it will use 3.36.z versions.

If multiple 3.34.z versions are available, the latest will be used. For example if 3.34.1 and 3.34.5 version are available, 3.34.5 will be used.

If any version of `version_priority` is available, then the most recent version found is used.

The environment variable `QDT_PREFERRED_QGIS_VERSION` is used as top priority if defined.

### search_paths

This option can be used to define search paths for QGIS installation. The order of the paths is used to define which path will be used in case of multiple installation for same QGIS version.

For example if you define:

```yaml
- name: Find installed QGIS
  uses: qgis-installation-finder
  with:
    - version_priority:
      - "3.36"
    - search_paths:
      - D:/Install/QGIS 3.36
      - D:/OtherInstall/QGIS 3.36
```

QDT will find two installation for version 3.36 but the first available in `search_paths` will be used (`D:/Install/QGIS 3.36` in our case).

### if_not_found

This option determines the action to be taken if QGIS is not found during the search process.

Possible_values:

- `warning` (_default_): if no version found, a warning is displayed in QDT logs
- `error`: if no version found, QDT stops and the other jobs are not run

----

## How does it work

On Linux, QDT locates installed QGIS with `which` command and will search for available installation with the `search_paths` option.

On Windows QDT tries to locate installed versions in the directories in `search_paths` option. If the option is not defined, QDT will search in these directories:

- `%PROGRAMFILES%\\QGIS x.y.z\` (by using a regexp to get available QGIS versions)
- `%QDT_OSGEO4W_INSTALL_DIR%` (default value : `C:\\OSGeo4W`)

By default, the most recent version found is used.

----

## Schema

```{eval-rst}
.. literalinclude:: ../schemas/scenario/jobs/qgis-installation-finder.json
  :language: json
```

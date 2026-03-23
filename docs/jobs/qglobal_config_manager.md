# QGIS global config manager

[`qgis_global_settings.ini` file](https://docs.qgis.org/latest/en/docs/user_manual/introduction/qgis_configuration.html#globalsettingsfile) contains global settings for all QGIS profile.

This jobs handles copy of a source .ini file to a destination .ini file and definition of `QGIS_GLOBAL_SETTINGS_FILE` environment variable so the file can be used by QGIS.

----

## Use it

Sample job configuration in your scenario file:

```yaml
  - name: Handle the qgis_global_settings.ini file
    uses: qglobal-config-manager
    with:
      src: ./global/qgis_global_settings.ini
      dst: ~/config/qgis/global_settings.ini
```

----

## Options

### src

Define source .ini file path. This can be an url, in this case, QDT download the .ini file in a local directory before copying to the destination.

`src` can be a relative path. In this case we check for .ini file related to:

- repository folder from current scenario
    - when the job `qprofiles-synchronizer` is run, all profiles repository are stored in a local repositories folder : `<qdt_working_folder>/respositories/<scenario_id>`
    - .ini file can be stored in profile repository and defined with a relative `src` : `./myprofile/qgis_global_settings.ini`
- qdt local working directory.
    - can be defined with `QDT_LOCAL_WORK_DIR` environment variable

The job fails if source .ini file doesn't exist or can't be downloaded.

### dst

Define destination .ini file path. The file path must be absolute.

If the source .ini file use environment variables, they are converted in destination .ini file.

## Default value

If no value defined in jobs, default values are used. The value is defined with the same behavior as QGIS :

- first use `QGIS_GLOBAL_SETTINGS_FILE`
- if not defined, use AppDataLocation folder:
    - Linux: `$HOME/.local/share/QGIS/QGIS3/`
    - Windows  : `C:\Users\<username>\%AppData%\Roaming\QGIS\QGIS3\`
    - MacOS : `$HOME/Library/Application Support/QGIS/QGIS3/`
- if file doesn't exists :
    - the installation directory, i.e.,  `your_QGIS_package_path/resources/qgis_global_settings.ini`
    - to define the QGIS package path we use `QDT_QGIS_EXE_PATH` environment variable

----

## How does it work

### Workflow

1. Check `src` definition (use default value / download from url / check if exists)
1. Copy `src` .ini file to `dst` .ini with environment variable conversion
1. Update `QGIS_GLOBAL_SETTINGS_FILE` environment variable with `dst` .ini file path

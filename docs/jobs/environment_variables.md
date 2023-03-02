# Environment variables manager

Use this job to set/delete environment variables. For example to set a value for a QGIS environment variable or to set a parameter that used by a plugin.

----

## Use it

Sample job configuration in your scenario file:

```yaml
- name: Set environment variables
    uses: manage-env-vars
    with:
        - QGIS_GLOBAL_SETTINGS_FILE:  # the name of environment variable
            action: add
            scope: user
            value: "\\SIG\\QGIS\\CONFIG\\qgis_global_settings.ini"
```

----

## Options

### action

Tell the job what to do with the environment variable:

Possible_values:

- `add`: add environment variable
- `remove`: remove environment variable

### scope

Level of the environment variable.

Possible_values:

- `system`: environment variable is set at system level. QDT needs to be run as administrator.
- `user`: environment variable is set at user level. Default value.

### value

Value to set to the environment variable.
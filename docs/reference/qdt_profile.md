# QDT Profile

## Rules

> Added in version 0.34

You can add rules to make the profile deployment conditional. In the following example, the profile will be deployed only on Linux:

```json
{
  "$schema": "https://raw.githubusercontent.com/qgis-deployment/qgis-deployment-toolbelt-cli/main/docs/schemas/profile/qgis_profile.json",
  "name": "only_linux",
  "folder_name": "qdt_only_linux",
  "description": "A QGIS profile for QDT with a conditional deployment rule.",
  "author": "Julien Moura",
  "email": "infos+qdt@oslandia.com",
  "qgisMinimumVersion": "3.34.0",
  "qgisMaximumVersion": "3.99.10",
  "version": "1.7.0",
  "rules": [
    {
      "name": "Environment",
      "description": "Profile is configured to run only on Linux.",
      "conditions": {
        "all": [
          {
            "path": "$.environment.operating_system_code",
            "value": "linux",
            "operator": "equal"
          }
        ]
      }
    }
  ]
}
```

The rules engine is based on [Python Rule Engine](https://github.com/santalvarez/python-rule-engine/) project whom rules syntax belongs to [JSON Rules Engine](https://github.com/CacheControl/json-rules-engine).

> Added in version 0.38

You can also deploy profiles based on environment variables. In the following example, the profile will be deployed only if `QDT_IS_GIS_ADMIN` exists:

```json
{
  "$schema": "https://raw.githubusercontent.com/qgis-deployment/qgis-deployment-toolbelt-cli/main/docs/schemas/profile/qgis_profile.json",
  "name": "only_gis_admin",
  "folder_name": "qdt_only_gis_admin",
  "description": "A QGIS profile for QDT with a conditional deployment rule for GIS admin",
  "author": "Julien Moura",
  "email": "infos+qdt@oslandia.com",
  "qgisMinimumVersion": "3.34.0",
  "qgisMaximumVersion": "3.99.10",
  "version": "1.7.0",
  "rules": [
    {
      "name": "QDT_IS_GIS_ADMIN exists",
      "description": "Deploy only if $env:QDT_IS_GIS_ADMIN exists",
      "conditions": {
        "all": [
          {
            "path": "$.env.QDT_IS_GIS_ADMIN",
            "operator": "not_equal",
            "value": ""
          }
        ]
      }
    }
  ]
}
```

By default, only prefixed variables can be used in rules. Default prefixes are `QDT_` and `QGIS_`. You can use your own prefixes in scenario settings:

```yaml
[...]

settings:
  RULES_VARIABLES_PREFIX: "QDT_,QGIS_,MYPREFIX_,MYOTHERPREFIX_"

[...]
```

You can by-pass prefix check by setting `RULES_ONLY_PREFIXED_VARIABLES` to `false` in scenario settings.

:::{warning}
Be careful if you allow all variables, as it could cause security issues.
:::

### Conditions and rules context

Rules is a set of conditions that use logical operators to compare values with context (a set of facts) which is exposed as a JSON object. Here comes the context for a Linux environment:

```{eval-rst}
.. literalinclude:: ./rules_context.json
  :language: json
```

To help you writing rules, QDT provides a [command to export rules context](../usage/cli.md#rules-context-export):

```sh
qdt export-rules-context -o qdt_rules_context.json
```

----

## Model definition

The project comes with a [JSON schema](https://raw.githubusercontent.com/qgis-deployment/qgis-deployment-toolbelt-cli/main/docs/schemas/profile/qgis_profile.json) describing the model of a profile:

```{eval-rst}
.. literalinclude:: ../schemas/profile/qgis_profile.json
  :language: json
```

With a submodel for plugin object:

```{eval-rst}
.. literalinclude:: ../schemas/profile/qgis_plugin.json
  :language: json
```

:::{tip}
To retrieve the ID of a plugin see [this page](../guides/howto_qgis_get_plugin_id.md).
:::

----

## Sample profile.json

```{eval-rst}
.. literalinclude:: ../../tests/fixtures/profiles/good_sample_profile.json
  :language: json
```

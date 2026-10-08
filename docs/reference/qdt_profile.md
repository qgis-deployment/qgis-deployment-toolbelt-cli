---
tags:
    - plugin
    - profile
    - QDT
    - QGIS
    - QGIS Deployment Toolbelt
    - rule
---

# QDT Profile

(qdt-reference-profiles-page)=

A QDT profile is a regular QGIS profile folder with a `profile.json` file at its root. QDT reads this file to identify, compare, filter and complete the profile during deployment.

> [!TIP]
> Since writing a JSON file from scratch is not recommended for mental health, it's better to:
>
> - start from [project's examples](https://github.com/qgis-deployment/qdt-examples-qgis-profiles)
> - get inspired by [public projects](https://github.com/qgis-deployment/qdt-examples-qgis-profiles)
> - use the [Profile Manager plugin for QGIS](https://qgis-deployment.github.io/profile_manager/usage/export_qdt.html)
> - add the `$schema` key pointing to the [JSON schema](#model-definition) to get completion and validation in your code editor.

## Attributes details

The _Optional_ column reflects the JSON schema, used for validation in code editors. QDT itself does not validate `profile.json` at runtime: missing attributes are ignored and unknown ones are silently dropped.

## alias

| Optional  | Default |
| :-------: | :-----: |
| `yes`     |         |

Profile's name in a human readable form, allowing special characters. Informative only: not used by QDT jobs.

### author

| Optional  | Default |
| :-------: | :-----: |
| `no`      |         |

Name of profile author and maintainer.

### description

| Optional  | Default |
| :-------: | :-----: |
| `yes`     |         |

Profile description. Informative only: not used by QDT jobs.

### email

| Optional  | Default |
| :-------: | :-----: |
| `no`      |         |

Contact email.

### folder_name

| Optional  | Default |
| :-------: | :-----: |
| `yes`     |         |

Name of the profile's directory in QGIS.

### icon

| Optional  | Default |
| :-------: | :-----: |
| `yes`     |         |

Path to the icon used by the [shortcuts manager job](../jobs/shortcuts_manager.md), relative to the profile's root folder. When set and the file exists, it takes precedence over the `icon` set in the scenario.

If a file with the same stem and the extension preferred by the operating system exists alongside (`.ico` on Windows, `.png` or `.svg` on Linux, `.icns` on macOS), it is used instead. Otherwise, the original file is used as is.

### name

| Optional  | Default |
| :-------: | :-----: |
| `no`      |         |

Profile name without any special characters. It's used:

- as the folder name of the installed profile (`QGIS/QGIS3/profiles/{name}`),
- to match the `profile` value used in scenario jobs (shortcuts, splash screen...), along with the name of the profile's folder in the source.

### qdtMinVersion

> Added in version 0.45

| Optional  | Default |
| :-------: | :-----: |
| `yes`     |         |

Optional attribute to state the minimum QDT version required to deploy the profile (following simple [SemVer](https://semver.org/)). If the running QDT is older than this, the profile is skipped during synchronization.

### qgisMaximumVersion

| Optional  | Default |
| :-------: | :-----: |
| `yes`     |         |

Maximum QGIS version where the profile can be deployed. It should comply with SemVer (`X.Y.Z`).

> [!IMPORTANT]
> Informative only for now: QDT reads it but does not filter profiles on it. Use [rules](#rules) to condition deployment.

### qgisMinimumVersion

| Optional  | Default |
| :-------: | :-----: |
| `yes`     |         |

Minimum QGIS version where the profile can be deployed. It should comply with SemVer (`X.Y.Z`).

> [!IMPORTANT]
> Informative only for now: QDT reads it but does not filter profiles on it. Use [rules](#rules) to condition deployment.

### splash

| Optional  | Default |
| :-------: | :-----: |
| `yes`     |         |

Path to the image used as QGIS splash screen, relative to the profile's root folder. Used by the [splash screen manager job](../jobs/splash_screen_manager.md).

### version

| Optional  | Default |
| :-------: | :-----: |
| `no`      |         |

Profile version. Must comply with SemVer (`X.Y.Z`).

Used by the [profiles synchronizer job](../jobs/profiles_synchronizer.md) to compare downloaded and installed profiles, depending on its `sync_mode`. If missing on either side, versions can't be compared.

### plugins

List of plugins to be installed in the profile.

Example for a plugin from the official repository:

```json
{
  "plugins": [
    {
      "name": "Profile Manager",
      "folder_name": "profile_manager",
      "official_repository": true,
      "plugin_id": 3547,
      "version": "0.7.4"
    }
  ]
}
```

#### folder_name

| Optional  | Default |
| :-------: | :-----: |
| `yes`     |         |

Name of the plugin folder once installed (`python/plugins/{folder_name}`). If not set, it's deduced from the download URL, then from the slugified `name`.

Also used to build the download URL for the official repository.

#### location

| Optional  | Default  |
| :-------: | :------: |
| `yes`     | `remote` |

Where the plugin archive is located: `remote` or `local`. Also accepted under the `type` key. Invalid values fall back to `remote`.

#### name

| Optional  | Default |
| :-------: | :-----: |
| `no`      |         |

Plugin name, as referenced in the source plugins repository.

#### official_repository

| Optional  | Default |
| :-------: | :-----: |
| `yes`     |         |

`true` if the plugin is published on [plugins.qgis.org](https://plugins.qgis.org/). Automatically set when `url` or `repository_url_xml` point to it.

When `true` and `url` is not set, the download URL is built from `folder_name` (or `name`) and `version`.

#### plugin_id

| Optional  | Default |
| :-------: | :-----: |
| `yes`     |         |

Plugin ID in the repository. Used to name the downloaded archive in QDT's cache.

> [!TIP]
> To retrieve the ID of a plugin see [this page](../guides/howto_qgis_get_plugin_id.md).

#### qgisMaximumVersion

| Optional  | Default |
| :-------: | :-----: |
| `yes`     |         |

Maximum QGIS version where the plugin can be installed.

> [!WARNING]
> Informative only: not yet used by QDT.

#### qgisMinimumVersion

| Optional  | Default |
| :-------: | :-----: |
| `yes`     |         |

Minimum QGIS version where the plugin can be installed.

> [!WARNING]
> Informative only: not yet used by QDT.

#### repository_url_xml

| Optional  | Default |
| :-------: | :-----: |
| `yes`     |         |

URL to the plugins repository XML file. Used with `folder_name` (or `name`) and `version` to build the download URL when `url` is not set.

#### upgrade_mode

> Added in version 0.41

| Optional  | Default |
| :-------: | :-----: |
| `yes`     | `keep`  |

By default, when upgrading a plugin, the new version is unpacked on top of the existing folder (`keep` mode). This works well in most cases but can cause issues when a plugin removes or renames files between versions: leftover files from the old version may remain and cause conflicts or unexpected behavior.

Setting `upgrade_mode` to `delete` on a plugin ensures a clean installation by removing the existing plugin folder before unpacking the new version. This is recommended for plugins that are known to have breaking changes between versions or that do not handle leftover files gracefully.

Example in `profile.json`:

```json
{
  "plugins": [
    {
      "name": "my_plugin",
      "version": "2.0.0",
      "official_repository": true,
      "upgrade_mode": "delete"
    }
  ]
}
```

Possible values:

- `keep` (default): existing plugin folder is kept, newer version is unpacked on top of it.
- `delete`: existing plugin folder is deleted before unpacking the new version.

#### url

| Optional  | Default |
| :-------: | :-----: |
| `yes`     |         |

Direct URI (URL, `file://` or local path) to the plugin archive (`.zip`). Takes precedence over the other ways to build the download URL.

#### version

| Optional  | Default  |
| :-------: | :------: |
| `yes`     | `latest` |

Version of the plugin to install. Used to build the download URL and to compare with the installed version. Set it explicitly.

### rules

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

> [!WARNING]
> Be careful if you allow all variables, as it could cause security issues.

#### Nested conditions

`all` and `any` can contain other `all` / `any` groups, so that you can combine conditions with both logical operators. In the following example, the profile is deployed from September 2026 to September 2027, or whenever `QDT_ATTENDEE` is set to `true`:

```json
{
  "rules": [
    {
      "name": "Event window or attendee",
      "description": "Deploy during the event period or if the attendee flag is set.",
      "conditions": {
        "any": [
          {
            "all": [
              {
                "path": "$.date.current_year",
                "operator": "equal",
                "value": 2026
              },
              {
                "path": "$.date.current_month",
                "operator": "greater_than_inclusive",
                "value": 9
              }
            ]
          },
          {
            "all": [
              {
                "path": "$.date.current_year",
                "operator": "equal",
                "value": 2027
              },
              {
                "path": "$.date.current_month",
                "operator": "less_than_inclusive",
                "value": 9
              }
            ]
          },
          {
            "path": "$.env.QDT_ATTENDEE",
            "operator": "equal",
            "value": "true"
          }
        ]
      }
    }
  ]
}
```

#### Conditions and rules context

Rules is a set of conditions that use logical operators to compare values with context (a set of facts) which is exposed as a JSON object. Here comes the context for a Linux environment:

```{eval-rst}
.. literalinclude:: ./rules_context.json
  :language: json
```

To help you writing rules, QDT provides a [command to export rules context](../usage/cli.md#export-rules-context):

```sh
qdt export-rules-context -o qdt_rules_context.json
```

----

## Model definition

The project comes with a [JSON schema](https://raw.githubusercontent.com/qgis-deployment/qgis-deployment-toolbelt-cli/main/docs/schemas/profile/qgis_profile.json) describing the model of a profile.

Put this line at the top of the `profile.json` to get completion and validation in your code editor:

```json
{
  "$schema": "https://raw.githubusercontent.com/qgis-deployment/qgis-deployment-toolbelt-cli/main/docs/schemas/profile/qgis_profile.json",
[...]
}
```

```{eval-rst}
.. literalinclude:: ../schemas/profile/qgis_profile.json
  :language: json
```

With a submodel for plugin object:

```{eval-rst}
.. literalinclude:: ../schemas/profile/qgis_plugin.json
  :language: json
```

----

## Sample profile.json

```{eval-rst}
.. literalinclude:: ../../tests/fixtures/profiles/good_sample_profile.json
  :language: json
```

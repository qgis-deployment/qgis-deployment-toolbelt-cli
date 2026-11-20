# Profiles Synchronizer

This job synchronizes installed profiles (those stored in QGIS profiles folder) from the downloaded ones (those stored in QDT local folder).

----

## Use it

Sample job configurations.

### Update or install profiles only with a newer version number

```yaml
- name: Synchronize installed profiles from downloaded ones
  uses: qprofiles-synchronizer
  with:
    sync_mode: only_new_version
```

### Systematically overwrite installed profile with downloaded one

```yaml
- name: Synchronize installed profiles from downloaded ones
  uses: qprofiles-synchronizer
  with:
    sync_mode: overwrite
```

### Mark synchronized profiles with QDT metadata

```yaml
- name: Synchronize installed profiles from downloaded ones
  uses: qprofiles-synchronizer
  with:
    sync_mode: only_new_version
    qdt_watermark: variables
```

----

## Vocabulary

### Profiles states

- `remote`: a profile stored outside the end-user computer, on a git repository, an HTTP server or a LAN drive. Typically: `https://gitlab.com/Oslandia/qgis/profils_qgis_fr.git`.
- `downloaded`: a profile downloaded into the QDT local working folder. Typically: `~/.cache/qgis-deployment-toolbelt/Oslandia/`.
- `installed`: a profile's folder located into the QGIS profiles folder and so accessible to the end-user through the QGIS interface. Typically: `~/.local/share/QGIS/QGIS3/profiles/default` or `%APPDATA%/QGIS/QGIS3/profiles/default`

----

## Options

### sync_mode

Synchronization mode to apply with profiles.

Possible_values:

- `only_missing` (_default_): only install profiles that does not exist locally
- `only_different_version`: only install profiles that does not exist locally and update those with a different version number (lesser or upper)
- `only_new_version`: only install profiles that does not exist locally and update those with a lesser version number
- `overwrite`: systematically overwrite local profiles

### qdt_watermark

Where to write QDT metadata in the settings file (`QGIS3.ini`, `QGIS4.ini`...) of every profile synchronized by the job.

Possible_values:

- `none` (_default_): nothing is written
- `section`: metadata are written in a dedicated `[QDT]` section
- `variables`: metadata are written in the `[variables]` section, as global expression variables. End-users see them in _Settings > Options > Variables_ and can use them in expressions (`@qdt_profile_version` in a print layout typically).

Written metadata:

| Key | Value |
| :-- | :---- |
| `qdt_profile_author` | `author` of the profile, from its `profile.json` |
| `qdt_profile_email` | `email` of the profile, from its `profile.json` |
| `qdt_profile_version` | `version` of the profile, from its `profile.json` |
| `qdt_profile_last_sync` | date and time of the last synchronization |
| `qdt_version` | version of QDT which synchronized the profile |

Example of result with `qdt_watermark: section`:

```ini
[QDT]
qdt_profile_author=GIS team
qdt_profile_email=gis-team@example.org
qdt_profile_last_sync=2026-11-20T14:32:05+01:00
qdt_profile_version=1.2.0
qdt_version=1.0.0
```

----

## How does it work

### INI files merge strategy

When a profile update is triggered with `sync_mode: only_new_version`, QDT does **not** blindly overwrite the installed profile. Instead, it runs a merge that preserves end-user data while applying administrator changes.

This applies to both `QGIS3.ini` and `QGISCUSTOMIZATION3.ini`.

#### Merge workflow

The merge follows these steps:

1. **Create a temporary directory** prefixed `QDT_merge_profile_<name>_`.
2. **Copy the downloaded profile** into that temporary directory. This is the starting state.
3. **Overwrite the temporary INI** with the currently installed one. The temporary directory now holds the user's existing settings.
4. **Merge the downloaded INI into the temporary INI**, section by section:
   - For every key present in **both** files with **different values**: the installed (user) value is saved into a `QDT_backup_<section>` section.
   - The downloaded (admin) value is then written, overwriting the installed one.
   - Keys present **only in the installed** file (e.g. `[Recent Projects]`) are untouched.
   - Keys present **only in the downloaded** file are added.
   - Environment variables (e.g. `$USER`) are converted at write time.
5. **Copy the merged result** back into the QGIS profile folder.

See the diagram below to have a graphical representation of this workflow:

```{mermaid}
---
title: QDT - QGIS*.ini merging strategy
---

flowchart TD
    A([Profile identified as outdated]) --> B[Create temp directory]
    B --> C[Copy downloaded profile into temp dir]
    C --> D{QGIS3.ini exists<br>in both profiles?}

    D -- Yes --> E[Copy installed QGIS3.ini<br>into temp dir]
    E --> F[merge_to: iterate sections<br>from downloaded INI]
    F --> G{Key exists in<br>both with different value?}
    G -- Yes --> H[Save installed value<br>into QDT_backup_&lt;section&gt;]
    H --> I[Write downloaded value]
    G -- No / only in downloaded --> I
    G -- Only in installed --> J[Keep installed value untouched]
    I --> K{More keys / sections?}
    J --> K
    K -- Yes --> G
    K -- No --> L

    D -- No --> L{QGISCUSTOMIZATION3.ini<br>exists in both?}

    L -- Yes --> M[Copy installed QGISCUSTOMIZATION3.ini<br>into temp dir]
    M --> N[merge_to on<br>QGISCUSTOMIZATION3.ini]
    N --> O

    L -- No --> O[Copy temp dir<br>back to installed profile folder]
    O --> P([Done])
```

#### Concrete example

Given the following `QGIS3.ini` files before synchronisation:

**Downloaded profile** (v2.0 - administrator-managed):

```ini
[qgis]
style=Fusion
iconSize=24
checkVersion=false
defaultProjectFileFormat=Qgz

[locale]
userLocale=fr_FR
overrideFlag=true

[variables]
created_with_qdt=true
current_user=$USER
env=production
```

**Installed profile** (v1.2 - end-user's machine):

```ini
[qgis]
style=Windows
iconSize=32
checkVersion=false
defaultProjectFileFormat=Qgz

[locale]
userLocale=fr_FR
overrideFlag=true

[Recent Projects]
projects\1\path=/home/alice/projects/mon_projet.qgz
projects\1\title=Mon projet

[variables]
created_with_qdt=true
current_user=alice
```

**Resulting merged `QGIS3.ini`** in installed profile:

```ini
[qgis]
style=Fusion           ; overwritten by downloaded value
iconSize=24            ; overwritten by downloaded value
checkVersion=false     ; identical, untouched
defaultProjectFileFormat=Qgz

[locale]
userLocale=fr_FR
overrideFlag=true

[Recent Projects]      ; section absent from downloaded profile, kept as-is
projects\1\path=/home/alice/projects/mon_projet.qgz
projects\1\title=Mon projet

[variables]
created_with_qdt=true
current_user=alice     ; $USER resolved to alice at write time
env=production         ; new key from downloaded profile, added

[QDT_backup_qgis]      ; auto-created: user values before overwrite
style=Windows
iconSize=32

[QDT_backup_variables] ; auto-created: user values before overwrite
current_user=alice
```

#### Key behaviours to keep in mind

- **admin wins on conflicts**: when the same key exists in both files with different values, the downloaded (admin) value always takes precedence.
- **user-only sections are preserved**: sections missing from the downloaded profile (e.g. `[Recent Projects]`, bookmarks, window geometries) are never touched.
- **backup sections are traceable**: every overwritten value is saved in `QDT_backup_<section>` so the previous state is always recoverable.
- **environment variables are converted at write time**: a value like `$USER` in the downloaded profile is converted to the actual username of the machine running QDT.
- **`overwrite` mode skips all of this**: with `sync_mode: overwrite`, the profile folder is copied without any merge nor backup sections. Use it only when you want a full reset of the installed profile.

> [!NOTE]
> The merge is applied to the QGIS settings file (`QGIS3.ini`, `QGIS4.ini`...) and `QGISCUSTOMIZATION3.ini` (but not the `QGISCUSTOMIZATION.xml` introduced in QGIS 4) when the **downloaded** profile ships them.
>
> If the **installed** profile does not have the file yet (typically for the first installation of the profile), the downloaded file is written as is, except that environment variables are interpolated. No `QDT_backup_<section>` is created in that case.

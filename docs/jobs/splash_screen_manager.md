# Splash screen manager

Use this job to set your custom splash screen image.

----

## Use it

Sample job configuration in your scenario file:

```yaml
- name: Set splash screen
  uses: splash-screen-manager
  with:
    action: create_or_restore
    strict: true
```

----

## Options

### action

Tell the job what to do with splash screens:

Possible_values:

- `create`: add splash screen if not set
- `create_or_restore`: add splash screen if not set and replace eventual existing one
- `remove`: remove splash screen

### strict

Check image size against QGIS recomendations: 600x300.

Possible values:

- `true`: fail if the image dimensions does not comply with QGIS recomendations.
- `false`: do not fail if the image dimensions does not comply with QGIS recomendations. A warning is logged.

----

## How does it work

### Specify the file to use in the `profile.json`

Add the image file to the profile folder and specify the relative filepath under the `splash` attribute:

```json
{
    [...]
    "email": "qgis@oslandia.com",
    "icon": "images/qgis_icon.ico",
    "splash": "images/splash_qgis-fr_600x287.png",
    [...]
}
```

### Store the image file under the default path

If the path is not specified into the `profile.json`, the job looks for the default filepath `images/splash.png`. If the file exists, it will be used as splash screen image

### Customization file

The splash screen is set in the UI customization file of the profile, whose format depends on the QGIS major version: see [UI customization](../guides/howto_qdt_handle_qgis_major_versions.md#ui-customization) in the guide about QGIS major versions.

### Workflow diagram

See the diagram below to have a graphical representation of this workflow:

```{mermaid}
---
title: QDT - Splash screen manager workflow
---

flowchart TD
    A([For each downloaded profile]) --> B[Get the installed profile<br>QGIS3.ini or QGIS4.ini]
    B --> C{action?}

    C -- remove --> RM[[Remove the splash screen]]
    C -- create / create_or_restore --> D[Rename the profile.json splash image<br>into splash.png if needed]
    D --> E{images/splash.png<br>exists?}
    E -- No --> F([Next profile])
    E -- Yes --> G{Image fits<br>605x305?}
    G -- No and strict --> H([SplashScreenBadDimensionsError])
    G -- Yes, or not strict --> I[Enable UI customization<br>in QGISn.ini]
    I --> SET[[Set the splash screen]]

    RM --> V
    SET --> V

    subgraph ROUTER [Target customization file]
        V{QGIS major<br>version?}
        V -- 3 --> INI3[Add or remove splashpath<br>in QGISCUSTOMIZATION3.ini]
        V -- 4 --> S{Set or remove?}
        S -- Remove --> RM4[Remove splashpath from the ini file<br>and splashPath from the XML file,<br>if they exist]
        S -- Set --> X{QGISCUSTOMIZATION.xml<br>exists?}
        X -- Yes --> XV{Readable, with a<br>Customization root tag?}
        XV -- Yes --> XU[Set enabled and splashPath,<br>keep items customized with QGIS]
        XV -- No --> XK([Error logged,<br>file left untouched])
        X -- No --> O{Ini file holds other<br>customizations?}
        O -- No --> XN[Create the XML file:<br>root items, enabled and splashPath]
        O -- Yes --> L[Warning, set splashpath in the ini file<br>for QGIS 4 legacy import]
    end
```

----

## Schema

```{eval-rst}
.. literalinclude:: ../schemas/scenario/jobs/splash-screen-manager.json
  :language: json
```

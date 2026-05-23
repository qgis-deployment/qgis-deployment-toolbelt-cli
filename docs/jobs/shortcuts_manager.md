# Shortcuts manager

Use this job to create shortcuts in desktop and/or start menu allowing the end-user opening QGIS with a profile.

----

## Use it

Sample job configuration in your scenario file:

```yaml
- name: Create shortcuts for profiles
  uses: shortcuts-manager
  with:
    action: create_or_restore
    include:
      - profile: conf_qgis_fr
        label: "QGIS - Conf QGIS FR"
        additional_arguments:
          - --lang fr
          - --noversioncheck
        desktop: false
        start_menu: true
        icon: "qgis_icon.ico"
      - profile: Oslandia
        label: "QGIS - Profil Oslandia"
        additional_arguments:
          - --code ~/.local/share/QGIS/QGIS3/script/qgis-constrained-settings.py
          - --noversioncheck
        desktop: true
        start_menu: true
        icon: "qgis_icon_oslandia.ico"
```

----

## Options

### action

Tell the job what to do with shortcuts:

Possible_values:

- `create`: add shortcut if not set
- `create_or_restore` (_default_): add shortcut if not set and replace eventual existing one
- `remove`: remove shortcut

### include

List of shortcuts to create.  
See below for the suboptions.

#### additional_arguments

Arguments to pass to QGIS executable. To know what it's possible run `qgis --help` in a terminal.

#### desktop

If true, create a desktop shortcut.

#### icon

Filename of the icon to use for the shortcut. The path is relative to the profile folder.
If not set, the defaut QGIS icon is used instead.

#### label

Text to display on the shortcut.

#### profile

Name of the profile to associate with the shortcut.

#### start_menu

If true, create a desktop in start menu.

----

## How does it work

### Specify the file to use in the `profile.json`

Add the image file to the profile folder and specify the relative filepath under the `icon` attribute:

```json
{
    [...]
    "email": "qgis@oslandia.com",
    "icon": "images/qgis_icon.ico",
    [...]
}
```

### Managing different icon format for every operating system

Although Microsoft Windows is the primary focus, QDT aims to be cross-platform and must therefore handle the specific requirements of each operating system. For example, shortcuts created on the desktop or in the Start menu require icons in `.ico` format for Windows, whereas `.png` or `.svg` formats are accepted on Linux.

Since its version 0.43, QDT includes an automatic selection of the most suitable appropriate icon format based on the target operating system.
If you aim to deploy profiles with shortcuts to different operating systems, you should store your shortcut icons in different formats. Typically:

```sh
profiles/Oslandia/images/
├── qgis_icon_oslandia.ico
├── qgis_icon_oslandia.png
└── splash.png
```

To convert icons in different formats, it is recommended to use an external service such as [Vert](https://vert.framatoolbox.org/convert/) or [Convertio](https://convertio.co/fr/svg-ico/). There is also a `icon_converter.py` tool in the scripts folder of QDT. It requires a `pip install pillow` and then it's usable as a CLI:

```sh
> python scripts/icon_converter.py --help
usage: icon_converter.py [-h] {ico2png,png2ico} ...

Convert between ICO and PNG formats.

positional arguments:
  {ico2png,png2ico}
    ico2png          Convert ICO to PNG.
    png2ico          Convert PNG to ICO.

options:
  -h, --help         show this help message and exit

Examples:
  icon_converter.py ico2png input.ico
  icon_converter.py ico2png input.ico --output output.png --size 128
  icon_converter.py png2ico input.png --output output.ico
```

----

## Schema

```{eval-rst}
.. literalinclude:: ../schemas/scenario/jobs/shortcuts-manager.json
  :language: json
```

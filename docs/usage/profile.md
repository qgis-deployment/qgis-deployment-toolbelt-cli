# Describe and prepare your QGIS profiles

QDT is designed to work with QGIS profiles that allow different configurations (plugins, connections, symbologies, expressions, templates, etc.) to be segmented for different uses on the same installation.

In order to avoid unnecessary duplication of code (typically that of the various plugins) or configuration files and to make deployment reproducible, QDT relies on a profile definition file: `profile.json`.

QDT expects to find this file in the folder of each profile stored in the source of synchronized profiles in the qprofiles-manager job.

## Publish them

3 options:

- on a remote Git repository (github.com, gitlab.com, GitLab instance...)
- on a local Git repository (a folder with a `.git` subfolder containing every Git internal stuff)
- on a web server through HTTP using a `qdt-files.json` - see guide: [how to publish on a HTTP server](../guides/howto_publish_http.md)

:::{tip}
Editing a profile.json file can be tricky and since it's a critical piece of the QDT workflow, the project provide some tooling to help writing and checking them: [How to automatically validate QDT files](../guides/howto_validate_profiles_scenarios.md).
:::

----

## Typical structure of a project with profiles

Given 3 profiles to be deployed: `advanced`, `beginner` and `readonly`. Here comes a typical organization of folders, subfolers and files into your repository:

```sh
qgis-profiles/
├── .git/
├── .gitignore
├── LICENSE
├── profiles
│   ├── .gitignore
│   ├── advanced
│   │   ├── images
│   │   │   ├── profile_advanced.ico
│   │   │   └── splash.png
│   │   ├── profile.json
│   │   └── QGIS
│   │       ├── QGIS3.ini
│   ├── beginner
│   │   ├── images
│   │   │   ├── profile_beginner.ico
│   │   │   └── splash.png
│   │   ├── profile.json
│   │   └── QGIS
│   │       ├── QGIS3.ini
│   │       └── QGISCUSTOMIZATION3.ini
│   └── readonly
│       ├── bookmarks.xml
│       ├── images
│       │   └── profile_readonly.ico
│       ├── profile.json
│       ├── project_default.qgs
│       └── QGIS
│           └── QGIS3.ini
│           └── QGISCUSTOMIZATION3.ini
├── qdt
│   └── scenario.qdt.yml
├── README.md
```

----

## Good practices and recomendations

- if you use a Git repository, store profiles in a subfolder not at the project root and specify the relative path in scenario
- do not store the entire profile folder, but only files that contans something specific to your profile (use a `.gitignore` file - see [below](#use-a-gitignore-file-to-exclude-folders-and-files-with-patterns))
- keep only the lines of `*.ini` files which are custom to your profile:
    - QGIS will fill them automatically if needed
    - it reduces the surface of possible conflicts when dealing to upgrade a profile

### Use a `.gitignore` file to exclude folders and files with patterns

#### What and why

A QGIS profile folder often contains a bunch of files. Some of these files might be temporary or generated automatically by your computer or QGIS, and you don't really want to include them when you're sharing your profile with others or storing it in a version control system like Git.

That's where the `.gitignore` file comes in. It's a special file that you can create in your profile folder, and it lists the names or patterns of files that you want Git (and compatible softwares) to ignore. When you tell Git to ignore certain files, it won't track them or include them when you share or save your profile.

For example, if your profile involves plugins or automatically generated preview images (projects thumbnails), you might want to ignore most of theses files and the other ones like compiled binaries or scripts (typically `*.pyc`...), log files, or temporary build files. By adding these file names or patterns to your `.gitignore` file, you keep your profile clean and avoid cluttering it with files that aren't essential for others to understand and work on your profile.

In summary, the .gitignore file helps you manage which files Git should ignore and not include when you're tracking changes in your profile. It's a helpful tool for keeping your version control system tidy and focused on the important parts of your work.

#### How

1. Create a `.gitignore` in your QDT folder
1. Add a file or folder path or pattern to exclude by line

Typical `.gitignore` content:

```gitignore
# -- QDT usual patterns --

# Common
!.gitkeep
*.log

# QGIS Profiles
profiles/*/python/plugins/
profiles/*/previewImages/
*.db
*.*~
```

#### Resources

- [gitignore explained on GitHub official documentation](https://docs.github.com/get-started/getting-started-with-git/ignoring-files)
- the [.gitignore file](https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/blob/main/examples/.gitignore) used in official examples from QDT repository

# Profiles Downloader

This job downloads remote profiles through different protocols to the local QDT working folder.

----

## Use it

Sample job configurations.

### **Remote** HTTP repository

```yaml
- name: Download profiles from remote HTTP server
  uses: qprofiles-downloader
  with:
    branch: main
    protocol: http
    source: https://organization.intra/qgis/qdt/
```

:::{note}
If you use the HTTP procotol, a `qdt-files.json` must be downloadable at the URL source. Typically: `https://organization.intra/qgis/qdt/qdt-files.json`.

See this guide on [how to generate the qdt-files.json](../guides/howto_publish_http.md#generate-the-qdt-filesjson-index-file).
:::

### Public **remote** git repository

```yaml
- name: Download profiles from remote Git server
  uses: qprofiles-downloader
  with:
    branch: main
    protocol: git_remote
    source: https://github.com/geotribu/profils-qgis.git
```

### **Local** git repository

```yaml
- name: Download profiles from local Git repository
  uses: qprofiles-downloader
  with:
    branch: main
    protocol: git_local
    source: file:///home/jmo/Git/Geotribu/profils-qgis
```

With repository on [UNC path](https://en.wikipedia.org/wiki/Path_(computing)#Uniform_Naming_Convention):

```yaml
- name: Download profiles from Git repository stored on a local and "hidden" network drive
  uses: qprofiles-downloader
  with:
    branch: main
    protocol: git_local
    source: file://\\srv-01\QDT$
```

----

## Vocabulary

### Profiles states

- `remote`: a profile stored outside the end-user computer, on a git repository, an HTTP server or a LAN drive. Typically: `https://gitlab.com/Oslandia/qgis/profils_qgis_fr.git`.
- `downloaded`: a profile downloaded into the QDT local working folder. Typically: `~/.cache/qgis-deployment-toolbelt/Oslandia/`.
- `installed`: a profile's folder located into the QGIS profiles folder and so accessible to the end-user through the QGIS interface. Typically: `~/.local/share/QGIS/QGIS3/profiles/default` or `%APPDATA%/QGIS/QGIS3/profiles/default`

----

## Options

### branch

Name of the branch to use when working with a git repository.

### protocol

Set which protocol to use.

Possible_values:

- `git_local`: use git to clone or pull changes from a repository accessible through filesystem, on the same computer or a shared drive on local network. `source` must end with `.git` and `branch` should also be set.
- `git_remote` (_default_): use git to clone or pull changes from a remote repository accessible through underlying HTTP protocol. `source` must end with `.git` and `branch` should also be set.
- `http`: use HTTP to download remote profiles. Source must start with `http`.

### source

Location of profiles to use as reference.

Must start with:

- `file://`: for local disk or network
- `git://` (_recomended_): for git repositories
- `https://`: for profiles stored into git repositories accessible through HTTP or profiles downloadable through an HTTP server

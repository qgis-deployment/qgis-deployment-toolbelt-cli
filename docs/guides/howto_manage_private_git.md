# How to make QDT work with a private Git repository

For now, QDT does not support private Git repositories. It's a "to be funded" issue. If you'd like to see this feature included in our functional scope, please don't hesitate to get in touch!

```{mermaid}
---
title: QDT workflow around a Git private forge (to be funded)
---

flowchart LR
    A["QGIS/QDT admin"] <---> |"classic git workflow<br/>clone/pull & git push"| D(("Private Git repository<br/>i.e. git.myorg.com or on GitHub/Lab"))
    D --->|"QDT"| F["QGIS end-user<br/>profiles"]
```

In the meantime, this isn't a critical limitation, as QDT supports local git repositories, i.e. stored on a network drive. Here comes a diagram illustrating the typical workflow used by most of end-users:

```{mermaid}
---
title: QDT workflow around a Git private forge (workaround)
---

flowchart LR
    A["QGIS/QDT admin"] <---> |"classic git workflow<br/>clone/pull & git push"| D(("Private Git repository<br/>i.e. git.myorg.com or on GitHub/Lab"))
    D -->|"Pull<br/>(with deployment token)"| E[["Server on local network<br/>i.e. '//gis/software/qgis/qdt/profiles/'"]]
    E --->|"QDT"| F["QGIS end-user<br/>profiles"]
```

To execute the intermediate git pull, the approach depends on the organization and GIS team habits. This can be done manually through the command-line, with a GUI like the excellent [GitHub Desktop](https://github.com/apps/desktop) or with a script. Below is an example PowerShell script for Windows.

## Sample script to synchronize a remote private Git project to a local server

> [!WARNING]
> This script is provided as a sample and may not fully comply with your environment or IT policies. Before implementing in production, take time to review and test it in your environment. If you make improvements or fixes, please share them.

### Requirements

- a service account
- [Git](https://git-scm.com/) >= 2.51 in the `PATH`
- [Git Credential Manager](https://microsoft.github.io/Git-Credential-Manager-for-Windows/Docs/CredentialManager.html) (usually shipped with Git for Windows)

### Configuration

It is configured through environment variables, typically set on the scheduled task running it:

| Key | Default value / example | Scope |
| :-- | :---------------------- | :---- |
| `QDT_GIT_USERNAME` | `gitlab+deploy-token-85` | Service account |
| `QDT_GIT_TOKEN` | `gldt-xxxxxxxxxxxxxxxxxxxx` | Service account |
| `QDT_LOCAL_CLONE_PROFILES_PATH` | `\\APPSGIS\QGIS\profiles\qdt-qgis-profiles` | Service account |
| `QDT_PROFILES_GIT_BRANCH` | `main` | Service account |
| `QDT_REMOTE_PROFILES_GIT` | `https://gitlab.myorg.com/gis/qdt-qgis-profiles.git` | Service account |

On GitLab, create a [deploy token](https://docs.gitlab.com/user/project/deploy_tokens/) on the project (*Settings* > *Repository* > *Deploy tokens*) with the `read_repository` scope only, and use its user name (`gitlab+deploy-token-{n}` unless customized) as `QDT_GIT_USERNAME`.

> [!IMPORTANT]
> Putting the token in the repository URL makess git store it in `<clone>\.git\config`, which every workstation of the fleet can read. The script sends it as a transient HTTP header instead.

```{eval-rst}
.. literalinclude:: ../../scripts/qdt_clone_pull_profiles.ps1
  :language: powershell
```

> [!TIP]
> The script exits with code `1` on any failure. Monitor it: an expired deploy token makes the synchronization fail silently otherwise, and the fleet keeps deploying the profiles frozen on that day.

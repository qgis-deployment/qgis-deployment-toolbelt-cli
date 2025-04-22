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

In the meanwhile, it's not a blocking lack, since QDT support local git repositories, i.e. stored on a network drive. Here comes a diagram illustrating the typical workflow used by most of end-users:

```{mermaid}
---
title: QDT workflow around a Git private forge (workaround)
---

flowchart LR
    A["QGIS/QDT admin"] <---> |"classic git workflow<br/>clone/pull & git push"| D(("Private Git repository<br/>i.e. git.myorg.com or on GitHub/Lab"))
    D -->|"Pull<br/>(with deployment token)"| E[["Server on local network<br/>i.e. '//gis/software/qgis/qdt/profiles/'"]]
    E --->|"QDT"| F["QGIS end-user<br/>profiles"]
```

To perform the intermediary git pull, it depends on the organization and GIS team habits. It can be performed manually through the command-line, with a GUI like the excellent [GitHub Desktop](https://github.com/apps/desktop) or with a script. We give below an example in PowerShell for Windows.

:::{info}
This script is a sample and might not comply with your environment and/or IT policy. If you intend to use it in production, take time to review it before. If you improve or fix it, please share it.
:::

```{eval-rst}
.. literalinclude:: ../../scripts/qdt_clone_pull_profiles.ps1
  :language: powershell
```

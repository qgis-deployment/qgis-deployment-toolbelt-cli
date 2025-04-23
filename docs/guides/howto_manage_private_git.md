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

:::{info}
This script is provided as a sample and may not fully comply with your environment or IT policies. Before implementing in production, take time to review and test it in your environment. If you make improvements or fixes, please share them.
:::

```{eval-rst}
.. literalinclude:: ../../scripts/qdt_clone_pull_profiles.ps1
  :language: powershell
```

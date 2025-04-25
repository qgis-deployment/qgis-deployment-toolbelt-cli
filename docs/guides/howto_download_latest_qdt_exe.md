# How to download the latest QDT's version

QDT comes with an upgrade command that check if a new version has been released in comparison with the used on, read the changelog and download the newest version: see [command-line usage](../usage/cli.md#upgrade-options).

Sometimes a system script fits better to usage, use-case or IT policy. We give below an example in PowerShell for Windows.

:::{info}
This script is a sample and might not comply with your environment and/or IT policy. If you intend to use it in production, take time to review it before. If you improve or fix it, please share it.
:::

You may need to change execution policy by running the following command in the same PowerShell terminal where you run the script:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
# alternatively, you can set it for your current user
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

```{eval-rst}
.. literalinclude:: ../../scripts/qdt_dowloader.ps1
  :language: powershell
```

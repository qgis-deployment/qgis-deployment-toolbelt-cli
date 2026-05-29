# Command-line interface usage

Aliases : `qdt`, `qgis-deployment-toolbelt`, `qdeploy-toolbelt`

## deploy

> Running a scenario deployment.

```{argparse}
  :module: qgis_deployment_toolbelt.cli
  :func: build_parser
  :path: deploy
  :prog: qdt
```

:::{tip}
This subcommand is defined as default. So `qdt -s [...]` is equivalent to `qdt deploy -s [...]`
:::

----

## export-rules-context

> Export rules context in a JSON file.

```{argparse}
  :module: qgis_deployment_toolbelt.cli
  :func: build_parser
  :path: export-rules-context
  :prog: qdt
```

----

## upgrade

:::{note}
Look for the latest released version and compare it with the running one.
:::

```{argparse}
  :description:
  :module: qgis_deployment_toolbelt.cli
  :func: build_parser
  :path: upgrade
  :prog: qdt
```

----

## completion

> Print instructions on enabling shell completions for QDT.
>
> If you encountered register-python-argcomplete command not found error, run:
>
> ```sh
> pipx install 'qgis-deployment-toolbelt[completion]'
> ```
>
> or if you already installed QDT with pipx:
>
>
> ```sh
> pipx inject qgis-deployment-toolbelt argcomplete
> ```
>
> - Bash: typically add to `~/.bashrc` or `~/.profile`:
>
>   ```bash
>   eval "$(register-python-argcomplete qdt)"
>   eval "$(register-python-argcomplete qgis-deployment-toolbelt)"
>   ```
>
> - zsh: to activate completions in zsh, first make sure `compinit` is enabled:
>
>   ```zsh
>   autoload -U compinit && compinit
>   ```
>
>   Afterwards you can enable completions:
>
>   ```zsh
>   eval "$(register-python-argcomplete qdt)"
>   ```
>
> - fish:
>
>   ```fish
>   register-python-argcomplete --shell fish qdt >~/.config/fish/completions/qdt.fish
>   ```
>
> - Powershell 5+:
>
>   ```powershell
>   register-python-argcomplete --shell powershell qdt | Out-String | Invoke-Expression
>   ```

:::{note}
CLI autocompletions are not available in "frozen" binaries in official releases.
:::

```{argparse}
  :module: qgis_deployment_toolbelt.cli
  :func: build_parser
  :path: completion
  :prog: qdt
```

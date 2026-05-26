# Command-line interface usage

Aliases : `qdt`, `qgis-deployment-toolbelt`, `qdeploy-toolbelt`

## deploy

:::{tip}
This subcommand is defined as default. So `qdt -s [...]` is equivalent to `qdt deploy -s [...]`
:::

```{argparse}
  :module: qgis_deployment_toolbelt.cli
  :func: build_parser
  :path: deploy
  :prog: qdt
```

## export-rules-context

```{argparse}
  :module: qgis_deployment_toolbelt.cli
  :func: build_parser
  :path: export-rules-context
  :prog: qdt
```

## upgrade

```{argparse}
  :module: qgis_deployment_toolbelt.cli
  :func: build_parser
  :path: upgrade
  :prog: qdt
```

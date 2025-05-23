# Configuration

## Using environment variables

### CLI arguments

Some options and arguments can be set with environment variables.

| Variable name                       | Corresponding CLI argument | Default value      |
| :---------------------------------- | :------------------------: | :----------------: |
| `QDT_LOGS_LEVEL`                    | `-v`, `--verbose` | `1` (= `logging.WARNING`). Must be an integer. |
| `QDT_PROXY_HTTP`                    | `--proxy-http` to customize network proxy to use. See also [How to use behind a proxy](../guides/howto_behind_proxy.md). | No proxy. |
| `QDT_SCENARIO_PATH`                 | `--scenario` in `deploy`   | `scenario.qdt.yml` |
| `QDT_UPGRADE_CHECK_ONLY`            | `-c`, `--check-only` in `upgrade`   | `False` |
| `QDT_UPGRADE_DISPLAY_RELEASE_NOTES` | `-n`, `--dont-show-release-notes` in `upgrade`   | `True` |
| `QDT_UPGRADE_DOWNLOAD_FOLDER`       | `-w`, `--where` in `upgrade`   | `./` (current folder) |

### Others

Some others parameters can be set using environment variables.

| Variable name       | Description            | Default value      |
| :------------------ | :----------------------: | :----------------: |
| `QDT_LOCAL_WORK_DIR` | Local folder where QDT download remote resources (profiles, plugins, etc.) | `~/.cache/qgis-deployment-toolbelt/default/` |
| `QDT_LOGS_DIR` | Folder where QDT writes the log files, which are automatically rotated. | `~/.cache/qgis-deployment-toolbelt/logs/` |
| `QDT_OSGEO4W_INSTALL_DIR` | Path to the OSGEO4W install directory. Used to search for installed QGIS and shortcuts creation. | `C:\\OSGeo4W`. |
| `QDT_QGIS_EXE_PATH` | Path to the QGIS executable to use. Used in shortcuts. | `/usr/bin/qgis` on Linux and MacOS, `%PROGRAMFILES%/QGIS 3.28/bin/qgis-ltr-bin.exe` on Windows. |
| `QDT_RULES_ONLY_PREFIXED_VARIABLES` | If set to `true`, only environment variables prefixed with prefixes listed in RULES_VARIABLES_PREFIX are considered in rules for security concerns. If set to `false`, all environment variables are considered in rules. | `true` |
| `QDT_RULES_VARIABLES_PREFIX` | List of prefixes of environment variables considered in rules. Only relevant if RULES_ONLY_PREFIXED_VARIABLES is set to `true`. The list is comma-separated. For example: `QDT_,QGIS_,MYPREFIX_`. | `QDT_,QGIS_` |
| `QDT_STREAMED_DOWNLOADS` | If set to `false`, the content of remote files is fully downloaded before being written locally. | `true` |
| `QDT_SSL_USE_SYSTEM_STORES` | By default, a bundle of SSL certificates is used, through [certifi](https://pypi.org/project/certifi/). If this environment variable is set to `true`, QDT tries to uses the system certificates store. Based on [truststore](https://truststore.readthedocs.io/). See also [How to use custom SSL certificates](../guides/howto_use_custom_ssl_certs.md).  | `False` |
| `QDT_SSL_VERIFY` | Enables/disables SSL certificate verification. Useful for environments where the proxy is unreliable with HTTPS connections. Boolean: `true` or `false`. | `True` |
| `QDT_PAC_FILE` | Define PAC file for proxy definition. See also [How to use behind a proxy](../guides/howto_behind_proxy.md). | `` |

----

## 3rd party environment variables

Some of the 3rd party environment variable applies to QDT:

| Variable name       | Description            |
| :------------------ | :----------------------: |
| `REQUESTS_CA_BUNDLE` | Set the path to the bundle of SSL certificates to use for HTTPS requests. See also [How to use custom SSL certificates](../guides/howto_use_custom_ssl_certs.md).  |
| `QGIS_CUSTOM_CONFIG_PATH` | Used to customize the path to the folder where QGIS stores the user's profiles. See [upstream documentation](https://docs.qgis.org/3.34/en/docs/user_manual/introduction/qgis_configuration.html#profiles-path). |

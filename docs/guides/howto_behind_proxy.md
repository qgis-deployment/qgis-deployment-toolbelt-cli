# How to use behind a network proxy

:::{note}
Only HTTP and HTTPS proxies are supported. No socks. Automatic values definition from PAC file available.
:::

> See [Requests official documentation](https://docs.python-requests.org/en/latest/user/advanced/#proxies)

## Passing as CLI option

- the proxy configuration is scoped to the QDT execution.
- it supports only one URL for both HTTP and HTTPS

```sh
qdt --proxy-http "http://user:password@proxyserver.intra:8765"
```

----

## Using environment variables

For proxy definition, QDT use this order of priority:

- `QDT_PROXY_HTTP`
- `QDT_PAC_FILE`
- PAC file from system
- Proxy configuration from system
- Generic `HTTP_PROXY` and `HTTPS_PROXY`

### Custom `QDT_PROXY_HTTP`

- it avoids potential conflict with "classic" proxy settings
- it allows to use a specific network proxy for QDT (can be useful for some well controlled systems)

### Use PAC file

[PAC file](https://developer.mozilla.org/en-US/docs/Web/HTTP/Proxy_servers_and_tunneling/Proxy_Auto-Configuration_PAC_file) can be used by SysAdmin to define proxy with a set of rules depending on the url.

[PyPac](https://pypac.readthedocs.io/en/latest/) is used for PAC file management. By default we are using the PAC file defined by system but a custom PAC file can be defined with `QDT_PAC_FILE` environment variable (local file or url).

### Generic `HTTP_PROXY` and `HTTPS_PROXY`

- it allows a specific URL by protocol (scheme)

#### Example on Windows PowerShell

Only for the QDT command scope:

```powershell
$env:QDT_PROXY_HTTP='http://user:password@proxyserver.intra:8765'; qdt -vvv
```

At the shell session scope:

```powershell
> $env:QDT_PROXY_HTTP='http://user:password@proxyserver.intra:8765'
> qdt -vvv
```

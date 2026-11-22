# Security Policy

Because QDT is meant to be carried out on large-scale IT infrastructures, security is one of the development challenges. It's enforced through automated checks, which are mainly executed in CI. You can also run the most of them manually.

## Automated security checks

- [GitGuardian](https://www.gitguardian.com/): detects secrets in the source code to help developers and security teams secure the modern development process.
- [Github Code QL](https://codeql.github.com/): GitHub integrated tool to discover vulnerabilities across a codebase
- [GitHub Immutable Releases](https://docs.github.com/code-security/supply-chain-security/understanding-your-software-supply-chain/immutable-releases)
- [Dependabot Alerts](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-supply-chain-security#what-is-dependabot): GitHub integrated tool that keeps dependencies up to date by informing of any security vulnerabilities in project's dependencies, and automatically opens pull requests to upgrade dependencies to the next available secure version when a Dependabot alert is triggered, or to the latest version when a release is published.
- [Dependabot cooldown](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference#configuration-of-cooldown): version updates of runtime dependencies are delayed (14 days for major releases, 10 days for minor and 7 days for patch ones) so that a compromised release has time to be detected before it reaches the builds. Security updates are not delayed.
- [GitHub secret scanning](https://docs.github.com/code-security/secret-scanning/secret-scanning-patterns#supported-secrets): integrated Github secrets scanning to receive alerts for detected secrets, keys, or other tokens.
- [Bandit](https://bandit.readthedocs.io): Bandit is a tool designed to find common security issues in Python code. Aslo executed for every commit as git hook.
- [Safety](https://pypi.org/project/safety/): Safety is a tool (part of PyUp security suite) designed to scan dependencies.

----

## Supported Versions

Only the latest released version of QDT receives fixes, including security ones. Previous versions are not patched: upgrading to the latest release is the way to get a fix.

This also applies to vulnerabilities in third-party dependencies, such as the CA certificates bundle ([certifi](https://pypi.org/project/certifi/)). The official executables embed their dependencies as they were at build time, so a new QDT release is published to ship the updated dependency.

----

## Security Advisories

Security advisories are published on the [repository's security page](https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/security/advisories) and mentioned in the release notes of the version fixing them.

----

## Dependencies relying on compiled code

QDT itself is pure Python, but some of its dependencies ship compiled binaries (`.pyd` on Windows, `.so` on Linux and macOS), installed from the wheels published on PyPI:

| Dependency | Language | Required by | Platforms | Usage in QDT |
| :--------- | :------- | :---------- | :-------- | :----------- |
| [charset-normalizer](https://pypi.org/project/charset-normalizer/) | Python compiled with Cython | [requests](https://pypi.org/project/requests/) | all | Detects the encoding of HTTP responses. The same modules are also shipped as pure Python, used when the binaries are missing. |
| [dukpy](https://pypi.org/project/dukpy/) | C ([Duktape](https://duktape.org/) JavaScript engine) | [pypac](https://pypi.org/project/pypac/) | all | Runs the proxy auto-configuration (PAC) JavaScript files. No pure Python fallback. |
| [dulwich](https://pypi.org/project/dulwich/) | Rust | QDT | all | Git implementation used to download profiles from Git repositories. The Rust extensions speed up objects, packs and trees handling, with a pure Python fallback when they're missing. Since its version 0.48.0, the official QDT executables install the pure Python version, so those Rust extensions are not embedded. |
| [pydantic-core](https://pypi.org/project/pydantic-core/) | Rust | [pydantic](https://pypi.org/project/pydantic/), required by [python-rule-engine](https://pypi.org/project/python-rule-engine/) | all | Validation core of pydantic, used to evaluate the profiles deployment rules. No pure Python fallback. |
| [pyobjc](https://pypi.org/project/pyobjc/) | Objective-C | [Send2Trash](https://pypi.org/project/Send2Trash/) (`nativeLib` extra) | macOS | Moves the deleted files to the macOS Trash. Send2Trash falls back on a ctypes implementation when it's missing. |
| [pywin32](https://pypi.org/project/pywin32/) | C/C++ | QDT, [python-win-ad](https://pypi.org/project/python-win-ad/), [Send2Trash](https://pypi.org/project/Send2Trash/) (`nativeLib` extra) | Windows | Windows APIs: shortcuts and COM objects, Active Directory user and groups (through python-win-ad), recycle bin. No fallback for QDT and python-win-ad usages. |
| [PyYAML](https://pypi.org/project/PyYAML/) | C (binding to [LibYAML](https://pyyaml.org/wiki/LibYAML)) | QDT | all | Reads the scenario files. QDT uses the pure Python loader (`yaml.safe_load`): the C extension is shipped but not used. |

These binaries are not signed (no Authenticode signature on Windows). In the official executables, built with [PyInstaller](https://pyinstaller.org/) as a single file, only the executable itself is signed: the embedded binaries are extracted to a temporary folder and loaded from there at each run. This matters on workstations where application control policies (AppLocker, WDAC...) restrict the libraries which can be loaded.

----

## Reporting a Vulnerability

Please report (suspected) security vulnerabilities to **[qgis+security@oslandia.com](mailto:qgis+security@oslandia.com)**. You will receive a response from us within 48 hours. If the issue is confirmed, we will release a patch as soon as possible depending on complexity but historically within a few days.

----

## Run security checks manually

Some checks can be executed on the developer side.

### Install dependencies related to security

```sh
python -m pip install -U -e .[security]
```

### Run Bandit check

In a terminal:

```sh
bandit --configfile pyproject.toml --format screen -r qgis_deployment_toolbelt
```

It's also possible to get results as a CSV:

```sh
bandit --configfile pyproject.toml --format csv --output bandit_report.csv -r qgis_deployment_toolbelt
```

Then open the `bandit_report.csv` file.

### Run Safety check

To run Safety CLI locally, an authenticated account is required:

```sh
safety auth
```

Then:

```sh
safety scan --full-report --output screen
```

It's also possible to get results as HTML:

```sh
safety scan --full-report --output html > safety_report.html
```

Then open the `safety_report.html` file.

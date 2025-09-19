# Security Policy

Because QDT is meant to be carried out on large-scale IT infrastructures, security is one of the development challenges. It's enforced through automated checks, which are mainly executed in CI. You can also run the most of them manually.

## Automated security checks

- [GitGuardian](https://www.gitguardian.com/): detects secrets in the source code to help developers and security teams secure the modern development process.
- [Github Code QL](https://codeql.github.com/): GitHub integrated tool to discover vulnerabilities across a codebase
- [GitHub Immutable Releases](https://docs.github.com/code-security/supply-chain-security/understanding-your-software-supply-chain/immutable-releases)
- [Dependabot Alerts](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-supply-chain-security#what-is-dependabot): GitHub integrated tool that keeps dependencies up to date by informing of any security vulnerabilities in project's dependencies, and automatically opens pull requests to upgrade dependencies to the next available secure version when a Dependabot alert is triggered, or to the latest version when a release is published.
- [GitHub secret scanning](https://docs.github.com/code-security/secret-scanning/secret-scanning-patterns#supported-secrets): integrated Github secrets scanning to receive alerts for detected secrets, keys, or other tokens.
- [Bandit](https://bandit.readthedocs.io): Bandit is a tool designed to find common security issues in Python code. Aslo executed for every commit as git hook.
- [Safety](https://pypi.org/project/safety/): Safety is a tool (part of PyUp security suite) designed to scan dependencies.

----

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for
receiving such patches depends on the CVSS v3.0 Rating.

For now, no vulnerability has been found.

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
bandit --configfile bandit.yaml --format screen -r qgis_deployment_toolbelt
```

It's also possible to get results as a CSV:

```sh
bandit --configfile bandit.yaml --format csv --output bandit_report.csv -r qgis_deployment_toolbelt
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

# CHANGELOG

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

<!--

Unreleased

## {version_tag} - YYYY-DD-mm

### Added

### Changed

### Removed

-->

## 0.40.0 - 2025-10-21

### Bugs fixes 🐛

* fix(logs): disable error raising about invalid repo by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/716>
* fix(qgis-finder): handle case where QDT_QGIS_EXE_PATH can be a (stringified) dict by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/732>

### Features and enhancements 🎉

* Minor logging improvements by @nicogodet in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/711>
* feature(shortcut): add context action on linux shortcut to allow profile removal by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/688>
* change(splash-screen): decrease log level from warning to info when an image is not fully compliant and if the strict mode is disabled by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/736>
* Allow to set selectionPolicy to 0, 1 or 2 for a full control by @nicogodet in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/712>

### Tooling 🔧

* Docs and upgrade: distinguish current version from last release by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/713>
* build(deps): update pytest-cov requirement from <7,>=4 to >=4,<8 by @dependabot[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/725>
* improve(ci): auto cancel concurrent workflow runs on same branch by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/728>
* build(deps): bump actions/checkout from 4 to 5 by @dependabot[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/721>
* build(deps): bump actions/setup-python from 5 to 6 by @dependabot[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/719>
* build(deps): bump codecov/codecov-action from 5.4.3 to 5.5.1 by @dependabot[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/717>
* build(deps): bump actions/download-artifact from 4 to 5 by @dependabot[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/720>
* build(deps): bump actions/upload-pages-artifact from 3 to 4 by @dependabot[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/718>
* build(deps): update pyinstaller requirement from <6.16,>=6.13 to >=6.13,<6.17 by @dependabot[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/724>
* build(deps): update dulwich requirement from <0.24.2,>=0.24.1 to >=0.24.1,<0.24.3 by @dependabot[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/723>
* [pre-commit.ci] pre-commit autoupdate by @pre-commit-ci[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/729>
* build(deps): bump actions/labeler from 5 to 6 by @dependabot[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/733>
* build(deps): update pillow requirement from <11.4,>=10.4.0 to >=10.4.0,<12.1 by @dependabot[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/734>
* build(deps): update dulwich requirement from <0.24.3,>=0.24.1 to >=0.24.1,<0.24.7 by @dependabot[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/735>

## 0.39.1 - 2025-09-26

### Bugs fixes 🐛

* fix(logs): downgrade pyad again to avoid logging conflicts by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/707>

### Features and enhancements 🎉

* change(tooling): replace black, flake8 and isort by ruff by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/706>

### Tooling 🔧

* improve(packaging): use setuptools_scm to define version from git by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/704>

## 0.39.0 - 2025-09-25

### Bugs fixes 🐛

* Fix: RemoteProfilesHandlerBase.list_remote_branches for newer versions of dulwich.porcelain by @nicogodet in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/701>

### Features and enhancements 🎉

* improve(shortcuts): support YAML compliant list of str for `additional_arguments` by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/695>
* add(packaging): sign Windows binary in CI by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/698>

### Tooling 🔧

* update(ci): do not run certains jobs in forks by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/702>

### Documentation 📖

* add(project): code of conduct by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/697>
* update(docs): add explicit license mention and organizations table by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/696>
* Docs: add how to check signed binary on Windows by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/699>

## 0.38.2 - 2025-09-19

### Tooling 🔧

* update(ci): split release creation in two steps to comply with Immutable Releases by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/692>

## 0.38.1 - 2025-09-19

> Publishing built packages for this version failed because of incompatibility with [GitHub Immutable Releases](https://docs.github.com/code-security/supply-chain-security/understanding-your-software-supply-chain/immutable-releases). See [0.38.2](#0382---2025-09-19).

### Bugs fixes 🐛

* Fix default profile setter page title in doc by @nicogodet in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/668>
* fix(docs): fix schema and add documentation for rules prefixes in scenario settings by @nicogodet in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/669>
* Packaging: use title as file description and description as comments for Windows Task Manager display name by @nicogodet in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/670>

### Features and enhancements 🎉

* improve(shortcut): add StartupWMClass=QGIS3 to improve GNOME dock integration by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/687>
* improve(shortcut): add StartupNotify=true to improve GNOME integration by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/689>

### Tooling 🔧

* fix(tooling): pytest config was conflicting in VS Code by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/686>
* build(deps): bump codecov/codecov-action from 5.4.2 to 5.4.3 by @dependabot[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/673>
* [pre-commit.ci] pre-commit autoupdate by @pre-commit-ci[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/679>
* build(deps): bump pywin32 from 310 to 311 by @dependabot[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/683>
* build(deps): update pyinstaller requirement from ==6.13.* to >=6.13,<6.16 by @dependabot[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/682>
* build(deps): update pillow requirement from <11.3,>=10.4.0 to >=10.4.0,<11.4 by @dependabot[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/676>
* build(deps): update python-rule-engine requirement from <0.6,>=0.5 to >=1.0,<1.1 by @dependabot[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/675>
* build(deps): update dulwich requirement from <0.22.9,>=0.22.5 to >=0.22.5,<0.24.2 by @dependabot[bot] in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/680>

### Documentation 📖

* Update logos by @sylvainbeo in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/684>
* update(docs): publicize Matrix channel by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/685>

### New Contributors

* @sylvainbeo made their first contribution in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/684>

## 0.38.0 - 2025-05-19

### Features and enhancements 🎉

* Allow usage of environment variables in rules path by @nicogodet in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/608>
* Store decoded branch name instead of bytes by @nicogodet in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/664>
* Packaging: switch to pyproject.toml by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/556>

### Bugs fixes 🐛

* improve(repository): fix some files leaking by @nicogodet in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/665>

## 0.37.1 - 2025-04-29

### Bugs fixes 🐛

* fix: correctly handle UNC paths by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/657>

### Tooling 🔧

* update(ci): set GH permission scope to improve security by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/656>

### Documentation 📖

* README: fix typos by @sguimmara in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/653>
* README: Add QDT logo by @sguimmara in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/654>

## 0.37.0 - 2025-04-28

### Bugs fixes 🐛

* update(ci): improve jobs conditions to fix documentation build by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/641>
* fix(ci): split build and deploy in 2 jobs by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/647>

### Features and enhancements 🎉

* Add new job "default-profile-setter" by @nicogodet in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/619>
* Extend default profile setter job with force_profile_selection_policy option by @nicogodet in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/648>
* improve(test): add case with a prefixed environment variable by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/646>

### Tooling 🔧

* update(security): bump security tooling versions and parameters by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/636>
* update(packaging): add Python 3.13 to tested and supported versions by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/642>

### Documentation 📖

* add(docs): how to make QDT work with private git repositories by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/634>
* add(docs): reference QDT active and known users by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/632>
* update(docs): Change the icons in the "They use QDT" section by @florentfougeres in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/633>
* update(docs): add ExecutionPolicy and parent folder creation to QDT downloader script by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/644>

**Full Changelog**: <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/compare/0.36.3...0.37.0>

## 0.36.3 - 2025-02-19

### Bugs fixes 🐛

* Let requests handle url encoding by @nicogodet in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/610>

## 0.36.2 - 2025-01-06

### Bugs fixes 🐛

* fix(test): make sure dl_url is a string by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/594>
* fix(proxy): HTTP_PROXY env variable was not removed after os_env_proxy wrapper by @jmkerloch in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/596>
* Fix schemas by @nicogodet in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/600>
* fix(docs): simplify JSON schema of job qgis-finder by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/601>
* Improve: automatically remove prefix from scenario env vars by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/605>

### Tooling 🔧

* Docs: update json schemas by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/559>
* update(ci): use macos-15 since macos-12 is deprecated by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/597>

### Documentation 📖

* add(docs): add script to download latest QDT version with PowerShell by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/595>

## 0.36.1 - 2024-11-29

### Bugs fixes 🐛

* fix(log): limit pyad to 0.6.2 for correct log level by @jmkerloch in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/586>
* fix(proxies): define environment variable for proxy use for git clone by @jmkerloch in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/584>

### Features and enhancements 🎉

* improve(plugins_sync): handle cases where a downloaded plugin is not a valid ZIP by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/577>
* feat(plugin download): add application/x-zip-compressed for header Accept by @jmkerloch in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/587>
* update(chore): move project under Github organization by @Guts in <https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/pull/589>

## 0.36.0 - 2024-10-08

### Bugs fixes 🐛

* fix(scenario): qgis-installation-finder accept if_not_found value warning and not warn. by @florentfgrs in <https://github.com/Guts/qgis-deployment-cli/pull/566>
* feat(pypac): add tldextract cache directory in pyinstaller by @jmkerloch in <https://github.com/Guts/qgis-deployment-cli/pull/564>

### Features and enhancements 🎉

* feat(pac): add file for tests by @jmkerloch in <https://github.com/Guts/qgis-deployment-cli/pull/562>
* feat(proxies): use pypac to use PAC file by @jmkerloch in <https://github.com/Guts/qgis-deployment-cli/pull/560>

## 0.35.3 - 2024-09-06

### Bugs fixes 🐛

* fix(profile sync): force copy if sync_mode is overwirte by @jmkerloch in <https://github.com/Guts/qgis-deployment-cli/pull/555>

### Features and enhancements 🎉

* Feature: support `search_paths` option in QGIS finder job by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/535>

### Documentation 📖

* update(docs): add how to use autogenerated release notes from GitHub by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/557>

## 0.35.2 - 2024-09-03

### Bugs fixes 🐛

* fix(downloader): stream option was not propagated to get args by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/550>
* fix(downloader): `qdt_plugins_to_copy` was not created in force mode by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/551>

### Features and enhancements 🎉

* add(tooling): helper script to convert png to ico by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/548>
* improve(downloader): use a custom HTTP transport adapter instead of rough injection by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/549>
* improve(tests): add scenario to test against plugins downloader in monothread and forced by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/552>

## 0.35.1 - 2024-09-02

### Features and enhancements 🎉

* feature(downloader): add option to disable SSL verification by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/544>

## 0.35.0 - 2024-09-02

### Features and enhancements 🎉

* refacto(cleanup): fix some type hints and relative imports by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/540>
* feature(downloader): add option to control over stream mode by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/541>
* Enhancement: rename shortcut module and improve docstring/type hints consistency by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/543>

### Tooling 🔧

* update(packaging): use Python 3.12 to build packages by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/542>

### Documentation 📖

* fix(docs): value must be quoted in PowerShell command to set env vars by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/536>

## 0.34.5 - 2024-06-06

### Bugs fixes 🐛

* fix(io): explicitly declare UTF-8 encoding in IO operations by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/520>

### Documentation 📖

* improve(docs): restore linkify (MyST parser extension) by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/516>

## 0.34.4 - 2024-05-30

### Bugs fixes 🐛

* Improve: qdt files reliability by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/514>

## 0.34.3 - 2024-05-29

### Bugs fixes 🐛

* Fix: rules context crash on certain Windows configuration by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/507>

### Features and enhancements 🎉

* improve(user_groups): enforces user domain groups retrieval using user guid by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/508>

### Tooling 🔧

* CI: test export rules context in different supported environments by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/512>

## 0.34.2 - 2024-04-25

### Bugs fixes 🐛

* fix(profiles): profiles listing was returning the unfiltered list by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/497>

### Documentation 📖

* Documentation: improve download section by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/496>

## 0.34.1 - 2024-04-24

### Features and enhancements 🎉

* feature(rules): on Windows, retrieve user extended data using win32 API by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/494>

## 0.34.0 - 2024-04-23

Killer feature introduced: rules engine. Funded by [Métropole du Grand Lyon](https://www.grandlyon.com/).

### Bugs fixes 🐛

* fix(logs): unreachable profile-attributes in logs by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/486>

### Features and enhancements 🎉

* Feature: add rules engine by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/481>
* Feature: add datetime to rules context by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/484>
* Feature: retrieve win32 user groups by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/393>
* feature(rules): add user name and groups to rules context by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/489>
* tests(usergroups): add unit tests against user groups module and update tests by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/490>
* Refacto: move profiles rules filter to generic class and use it systematically in jobs by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/487>
* Refacto: move rules context into a structured object by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/491>
* feature(cli): add command to export rules context in current environment by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/492>

### Tooling 🔧

* enhancement: improve reliability of version templater making sure that a SemVer compliant version number is passed by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/483>

### Documentation 📖

* Docs: add local test qdt by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/488>
* Docs: add rules context dynamically by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/485>

## 0.33.0 - 2024-04-05

### Features and enhancements 🎉

* feat(installed qgis): add qgis-installation-finder job by @jmkerloch in <https://github.com/Guts/qgis-deployment-cli/pull/464>

## 0.32.1 - 2024-04-02

### Bugs fixes 🐛

* fix(env variable): update local environment by @jmkerloch in <https://github.com/Guts/qgis-deployment-cli/pull/455>

### Tooling 🔧

* Tooling: add config for markdown files in VS Code  by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/461>

### Documentation 📖

* docs: fix autobuild command by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/462>
* docs: minor fixes by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/467>
* docs: complete validation tooling by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/463>
* docs: add quickstart by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/468>
* docs: remove pattern from JSON schemas by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/456>
* docs: add how to check using git hooks by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/457>
* docs: add robots.txt for SEO engines by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/458>
* docs: enable zoom in mermaid diagrams by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/459>
* docs: autodoc **init** functions by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/460>
* docs: add a page referencing QDT projects by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/465>
* docs: move how to publish to an HTTP server in a specific guide page by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/466>

## 0.32.0 - 2024-03-22

### Bugs fixes 🐛

* fix: remove deprecated job and fix minor confusing refs in JSON schemas by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/449>

### Features and enhancements 🎉

* feat(env variable): add write of environnement variable in .ini files from QDT profile by @jmkerloch in <https://github.com/Guts/qgis-deployment-cli/pull/452>

### Tooling 🔧

* packaging: set Python min/max versions by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/447>

### Documentation 📖

* demo: renew shortcuts profiles icons and add versions compatible with QGIS profiles list by @sylvainbeo and @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/453>

### Other Changes

* deps: bump minimal versions for git sync by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/443>

### New Contributors

* @jmkerloch and @sylvainbeo made their first contribution

----

## 0.31.2 - 2024-03-01

### Bugs fixes 🐛

* Fix: shortcut template was bundled to the wrong path by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/442>

### Features and enhancements 🎉

* refacto: rm typing_extensions from deps replacing by future.annotations by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/441>
* Feature: network use native system stores by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/444>

## 0.31.1 - 2024-02-23

### Bugs fixes 🐛

* fix: restore refresh_environment by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/438>

## 0.31.0 - 2024-02-23

### Features and enhancements 🎉

* refacto: remove unused methods and improve doctsrings by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/429>
* Refacto: split profiles sync job by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/432>
* Feature: job environment variables support linux by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/435>

### Tooling 🔧

* ci: use codecov upload token by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/430>
* ci: tag codecov uploads with CI matrix vars by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/431>
* tooling: ignore dev scripts and fixtures from Sonar analisis by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/433>
* ci: disable matrix fail fast by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/434>
* tooling: make sonar ignore tests for duplication by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/436>

## 0.30.2 - 2024-02-22

### Features and enhancements 🎉

* Improve: cleanup OSConfig and refacto CLI's tests to run outside real QGIS profiles folder by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/427>

## 0.30.1 - 2024-02-20

### Bugs fixes 🐛

* fix: undefined variable on Windows if scope != user by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/392>
* fix: change refs to menu_from_projects to match new versioning scheme by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/424>

### Features and enhancements 🎉

* Refacto: factorize logs folders retrieval by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/398>
* fix: tests were failing because of upstream URL change by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/409>
* Feature: log details about Certificates Authority bundle by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/397>
* tests: improve downloader testing by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/412>
* Improve: testing ini files against untracked files by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/416>
* Improve: refacto operating system constants retrieval by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/421>

### Tooling 🔧

* CI: update autolabeler to v5 by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/411>
* tooling: enable import autocompletion in VSCode by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/422>

### Documentation 📖

* docs: clean up and fix some syntax errors by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/420>
* docs: add custom qgis profiles folderpath with QGIS_CUSTOM_CONFIG_PATH by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/423>
* docs: add example on run QDT behind a proxy with PowerShell by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/394>
* docs: fix typo spotted by @sylvainbeo by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/395>
* docs: release upper pins of dependencies to reduce dependabot noise by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/417>
* docs: enable social cards by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/418>
* docs: add sitemap by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/419>
* docs: add new plugin's id retrieval method and reorganize the table of contents by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/425>

### Other Changes

* security: bump pillow to 10.2 to fix CVE-2022-22817 by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/400>

## 0.30.0 - 2023-12-29

### Bugs fixes 🐛

* Fix: splash screen removal by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/381>

### Features and enhancements 🎉

* Security: increase security scans and improve related documentation by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/352>
* Feature: download from http (part 1) by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/351>
* feature: add util to get ProxyHandler and cache some recurring functions by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/358>
* feature: use proxy handler in file downloader by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/359>
* feature: add simple http client by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/360>
* improvement: use proxy handle in upgrade sub-command by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/362>
* log: on Linux, add distribution name and version by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/363>
* log: add details about how QDT working folder is determined by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/364>
* Change: move QDT subfolders to generic job by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/347>
* Refacto: use requests to download files by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/367>
* Refacto: remove dead code by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/368>
* Feature: add file size to downloader log by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/369>
* Feature: add log filepath on exit error by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/370>
* feature: HTTP downloader refacto part 2 by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/372>
* feature: add function name to log by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/380>
* tests: add more scenarii and factorize test by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/382>
* feature: QdtProfile has now shortcuts to access to ini files and its installed alter-ego by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/383>
* Feature: improve splash screen manager logic by using ini helper intensively by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/384>

### Tooling 🔧

* tooling: add SonarCloud configuration file by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/378>

### Documentation 📖

* docs: improve development guide by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/357>
* docs: update qprofiles-manager with deprecated 'git' value by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/361>
* tooling: add SonarCloud badge by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/371>

## 0.30.0-beta2 - 2023-12-29

### Features and enhancements 🎉

* Refacto: use requests to download files by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/367>
* Refacto: remove dead code by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/368>
* Feature: add file size to downloader log by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/369>
* Feature: add log filepath on exit error by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/370>
* feature: HTTP downloader refacto part 2 by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/372>

### Tooling 🔧

* tooling: add SonarCloud configuration file by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/378>

### Documentation 📖

* tooling: add SonarCloud badge by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/371>

## 0.30.0-beta1 - 2023-12-26

### Features and enhancements 🎉

* Security: increase security scans and improve related documentation by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/352>
* Feature: download from http (part 1) by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/351>
* feature: add util to get ProxyHandler and cache some recurring functions by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/358>
* feature: add simple http client by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/360>
* improvement: use proxy handle in upgrade sub-command by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/362>
* log: on Linux, add distribution name and version by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/363>
* log: add details about how QDT working folder is determined by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/364>
* Change: move QDT subfolders to generic job by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/347>
* feature: use proxy handler in file downloader by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/359>

### Documentation 📖

* docs: improve development guide by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/357>
* docs: update qprofiles-manager with deprecated 'git' value by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/361>

## 0.29.0 - 2023-11-16

### Bugs fixes 🐛

* Fix: local Git repository were not recognized anymore as valid git repository <https://github.com/Guts/qgis-deployment-cli/issues/344>
* Fix: surround profile name with quotes to prevent space by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/348> (<https://github.com/Guts/qgis-deployment-cli/issues/320>)

### Features and enhancements 🎉

* Git synchronization: global improvements by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/346>

### Tooling 🔧

* CI: fix packages-dir path for PyPi upload by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/339>
* Packaging: add operating system name to build report by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/340>
* CI: avoid uploading build reports by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/341>

### Documentation 📖

* Docs: how to manually deploy to PyPi by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/342>

## 0.28.0 - 2023-11-14

### Bugs fixes 🐛

* Disable ConfigParser strict mode to better handling of heterogeneity of QGIS config files by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/334>

### Features and enhancements 🎉

* Add util to format octets size into human-readable format by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/331>
* Refacto: add a Git handler base class to inherit from and avoid duplicate code by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/333>
* Jobs: make downloaded and installed profiles listing more generic by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/336>
* Enhancement: add a module to read and write QGIS ini files by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/337>

### Tooling 🔧

* Packaging: renamed license to match Pypi classifier by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/326>
* Publishing to PyPi: switch to trusted publisher by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/327>
* Add python 3.12 to tests and supported versions by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/328>
* Packaging: restore operating system name in final executables by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/329>
* CI: add discussion category name to link to a GitHub Release by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/330>

### Documentation 📖

* Add demonstration profile viewer mode by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/332>

## 0.27.0 - 2023-11-08

### Bugs fixes 🐛

* Fix missing shortcut template in packaging by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/319>

### Features and enhancements 🎉

* Support custom HTTP proxy setting: QDT_PROXY_HTTP by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/293>
* Refacto: move shortcuts related code into specific subpkg by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/324>
* Quality: global project improvements and clean up by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/325>

### Tooling 🔧

* Improve setup: add extras and factorize requirements loading by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/302>
* Switch license from LGPL3 to Apache License 2 by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/314>
* Packaging: improve output name and PyInstaller options by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/321>
* Tooling: update VS Code config by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/323>

### Documentation 📖

* Mise à jour documentation by @sigeal in <https://github.com/Guts/qgis-deployment-cli/pull/315>

### Other Changes

* Update Pillow to fix CVE related to libwebp by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/313>

## New Contributors

* @sigeal made their first contribution in <https://github.com/Guts/qgis-deployment-cli/pull/315>

**Full Changelog**: <https://github.com/Guts/qgis-deployment-cli/compare/0.26.0...0.27.0>

## 0.26.0 - 2023-06-11

### Bugs fixes 🐛

* Fix: accept different types (URLs or str) as environment variables values by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/291>

## 0.25.0 - 2023-06-13

### Bugs fixes 🐛

* Set download as default action by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/281>

### Features and enhancements 🎉

* Improve: if icon not found, use default QGIS icon (only Linux Free Desktop) by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/282>

### Tooling 🔧

* Packaging: add icon to exe by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/285>

### Documentation 📖

* Add demo profile by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/276>
* Documentation: add typical project structure section by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/280>

## 0.24.0 - 2023-05-30

### Features and enhancements 🎉

* Upgrade: download new release binary only in frozen mode by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/266>

### Tooling 🔧

* Docs: deploy only on tags or main by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/265>
* Add feature request issue form by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/272>
* Packaging: publish QDT as Docker image in GHCR by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/274>

### Documentation 📖

* Add job to generate dependencies graph by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/267>
* Complete user manual by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/268>

## 0.23.1 - 2023-05-07

### Bugs fixes 🐛

* Set dulwich minimal version to prevent upstream bug (<https://github.com/jelmer/dulwich/pull/1164>) by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/263>

### Features and enhancements 🎉

* Improve log message during plugin version comparison by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/257>

## 0.23.0 - 2023-04-14

### Features and enhancements 🎉

* Quality: extends tests against file downloader util by @florentfgrs in <https://github.com/Guts/qgis-deployment-cli/pull/245>
* Feature: handle local Git repository by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/255>
* Feature: handle "local" plugins by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/253>

### Documentation 📖

* Docs: use glob to automatically include jobs docs in toctree by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/254>

### New Contributors

* @florentfgrs made their first contribution in <https://github.com/Guts/qgis-deployment-cli/pull/245>

## 0.22.3 - 2023-03-12

* Use QGIS LTR 3.28.4 path as default by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/243>

## 0.22.2 - 2023-03-12

### Features and enhancements 🎉

* Refacto: jobs splash screen and some mutualized methods by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/242>

## 0.22.1 - 2023-03-11

### Bugs fixes 🐛

* Fix: env var obfuscated by lru cache by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/236>
* Fix missing return profile object in shortcut job by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/239>
* Fix and refactoring get_qgis_path which was failing because of bad type passed to ast.literal_eval by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/241>

### Features and enhancements 🎉

* Improvement: make remote scenario downloaded a separate func by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/238>
* Feature: check path now try to expand user vars by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/240>

## 0.22.0 - 2023-03-10

### Features and enhancements 🎉

* Refacto: job shortcuts now use mutualized objects and tools by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/230>
* Feature: add line number to log to make debug easier by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/231>
* Feature: better logging by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/233>
* Improve how invalid YAML files are handled by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/234>
* Improvement: extract name and path from URL of remote scenario and store it properly in QDT work dir by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/235>

## 0.21.3 - 2023-03-09

### Bugs fixes 🐛

* Add default subparser to allow direct run of deployment by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/229>

## 0.21.2 - 2023-03-09

### Bugs fixes 🐛

* Fix unexpected keyword argument 'profiles_folder_to_copy' by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/227>

### Features and enhancements 🎉

* Improve reliability of profiles sync with only_missing by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/228>

## 0.21.1 - 2023-03-09

### Bugs fixes 🐛

* Hotfix crash when some profiles have a lesser version by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/226>

## 0.21.0 - 2023-03-09

### Bugs fixes 🐛

* Fix: outdated profiles should also be copied when sync_mode=only_different by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/225>

### Features and enhancements 🎉

* Improve upgrade subcommand by handling GitHub Token by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/219>
* Tooling: complete JSON schemas and job documentation by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/224>

### Tooling 🔧

* Add bug report issue form by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/222>

### Documentation 📖

* Documentation: improve download page by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/220>

## 0.20.0 - 2023-03-07

### Features and enhancements 🎉

* Tooling: add pyupgrade as git hook by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/218>
* Profiles synchronization: add sync_mode option by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/97>

### Documentation 📖

* Add funding page by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/217>

## 0.19.0 - 2023-03-03

### Features and enhancements 🎉

* Refacto: remove unused modules (dead code) by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/207>
* Improve: test coverage bouncer by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/209>
* Switch to a generic Job object with inheritance by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/208>
* Clean up: rm former validations methods by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/210>
* Tooling: add ruff to git hooks by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/211>
* Feature: use environment variables to set arguments values by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/215>
* Feature: support remote scenario path by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/216>

### Documentation 📖

* Documentation: add how to grab a plugin_id by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/214>

## 0.18.0 - 2023-03-02

### Bugs fixes 🐛

* Fix message when there is no newer version by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/205>

### Features and enhancements 🎉

* Add helper to handle common error on exe name by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/206>
* Feature: job to manage environment variables now handles `remove` action by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/199>

### Documentation 📖

* Add doc page about environment variable job by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/198>

## 0.17.0 - 2023-02-28

A version focused on refacto to reduce external dependencies.

### Features and enhancements 🎉

* Refacto: clean up rm unused subcmd by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/192>
* Refacto: replace click by argparse by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/194>
* Refacto: remove dependency to py-setenv by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/196>
* Refacto: remove rich dependency by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/197>

### Tooling 🔧

* Packaging: build and package for MacOS (experimental) by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/195>

## 0.16.2 - 2023-02-23

### Bugs fixes 🐛

* Fix QGIS bin path retriever by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/191>

### Features and enhancements 🎉

* Tooling and documentation: JSON schema for profile editing by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/187>

### Documentation 📖

* Documentation: fix build and switch to Furo theme by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/188>

## 0.16.1 - 2023-01-30

### Bugs fixes 🐛

* Embed shortcut template into packages by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/181>

### Features and enhancements 🎉

* Tooling: upgrade JSON schemas by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/180>
* Feature: upgrade show changelog by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/179>

## 0.16.0 - 2023-01-27

### Features and enhancements 🎉

* Dependencies: replace semver by packaging to compare versions by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/177>
* Feature: improve shortcut manager to create shortcuts on Linux (FreeDesktop) by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/178>

## 0.15.0 - 2023-01-26

### Features and enhancements 🎉

* Feature: plugins synchronization part 3 - Upgrade older plugins by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/176>

## 0.14.1 - 2023-01-21

### Bugs fixes 🐛

* Fix: download URL should use folder_name when exists instead of name by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/175>

## 0.14.0 - 2023-01-21

### Features and enhancements 🎉

* Feature: add a subcommand to upgrade the CLI by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/169>
* Feature: plugins downloader by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/168>
* Feature: plugins synchronization - part 1 by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/172>
* Feature: plugins synchronization part 2 by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/174>

### Tooling 🔧

* CI: build Python wheel using build package by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/170>
* Use GE to deploy to GH Pages instead of branch gh-pages by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/171>
* Set minimal Python to 3.10 by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/173>

## 0.13.0 - 2023-01-16

### Features and enhancements 🎉

* Add module to check image size by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/151>
* Add test for utils.slugifier by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/165>
* Improve test coverage on check image by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/166>
* Increase test coverage by @vicente23 in <https://github.com/Guts/qgis-deployment-cli/pull/157>
* Feature: add option to check splash screen dimensions by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/167>

## 0.12.0 - 2022-11-26

### Bugs fixes 🐛

* Replace the variable scenario by scenario_filepath by @vicente23 in <https://github.com/Guts/qgis-deployment-cli/pull/148>
* Check the validity of the scenario file by @vicente23 in <https://github.com/Guts/qgis-deployment-cli/pull/149>
* Make the remote git handler much more robust to  by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/154>

### Features and enhancements 🎉

* Allow to specify branch to clone/pull by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/152>
* Make logging binary : warning or debug by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/155>
* Add utils module to check paths in a centralized way by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/156>

### Tooling 🔧

* Fix documentation build on CI by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/144>
* Packaging: Add Python 3.11 to supported versions by @Guts in <https://github.com/Guts/qgis-deployment-cli/pull/153>

## 0.11.0 - 2022-11-16

* Add new job to manage custom splash screen
* Fix: job shortcut-manager was failing when icon is not defined
* Bump dependencies

## 0.10.0 - 2022-05-25

* Minor bug fixes
* Extends unit tests (65%)

## 0.9.0 - 2022-05-18

* handle `~` char in scenario files to represent the end-user home folder
* add [`utils.str2bool`](https://guts.github.io/qgis-deployment-cli/_apidoc/qgis_deployment_toolbelt.utils.str2bool.html) to convert `str` to `bool`. Useful to process environment variables which are always stored/retrieved as strings.
* add [`utils.win32utils.get_environment_variable`](https://guts.github.io/qgis-deployment-cli/_apidoc/qgis_deployment_toolbelt.utils.win32utils.html) to retrieve environment variable directly from Windows registry, because `os.getenv` uses the configuration at the run moment
* Documentation: add an auto-generated table of dependencies and their license within the [Credits page](https://guts.github.io/qgis-deployment-cli/misc/credits.html)
* Fix a bug when the icon path was not set for a shortcut
* Extend unit tests to reach 60% of coverage

> See the [GitHub Release for a detailed changelog](https://github.com/Guts/qgis-deployment-cli/releases/tag/0.9.0).

## 0.8.0 - 2022-05-16

* Pin dulwich version to avoid recurring connection errors
* Add support for environment variable `QGIS_CUSTOM_CONFIG_PATH`
* Make clone/pull more robust
* Extend unit tests

> See the [GitHub Release for a detailed changelog](https://github.com/Guts/qgis-deployment-cli/releases/tag/0.8.0).

## 0.7.0 - 2022-05-16

* Add module to create and delete application shortcuts
* Add job to use the new module to automatically create shortcuts for QGIS profiles
* Promote constants module to a dataclass (Python 3.7+)
* Remove subcommand to set environment variables
* Rename `environment_variables` section to `settings` in scenario files
* Handle situation where the QGIS profiles folder doesn't exist
* Fix the default QGIS profiles path on Windows
* Fix environment variables manager
* Fix and improve clean command
* Run unit tests on multiple operating systems: MacOS, Ubuntu LTS and Windows 10

> See the [GitHub Release for a detailed changelog](https://github.com/Guts/qgis-deployment-cli/releases/tag/0.7.0).

## 0.6.0 - 2022-05-10

* Profiles synchronization now handle the mixed case where some of downloaded profiles are already installed, and some are not.
* Extend unit tests
* Minor clean up

> See the [GitHub Release for a detailed changelog](https://github.com/Guts/qgis-deployment-cli/releases/tag/0.6.0).

## 0.5.0 - 2022-05-09

* Improve profiles synchronization logic by filtering on folders which are (or seem to be) QGIS profiles
* Minor changes

> See the [GitHub Release for a detailed changelog](https://github.com/Guts/qgis-deployment-cli/releases/tag/0.5.0).

## 0.4.0 - 2022-05-06

* Deploy: install downloaded profiles into a fresh QGIS install
* Check: operaing system compatibility
* Improve isort and codecov configurations

> See the [GitHub Release for a detailed changelog](https://github.com/Guts/qgis-deployment-cli/releases/tag/0.4.0).

## 0.3.0 - 2022-05-05

* Add Python Wheel as packaging option
* Deploy release to Python Package Index
* Complete and improve documentation

> See the [GitHub Release for a detailed changelog](https://github.com/Guts/qgis-deployment-cli/releases/tag/0.3.0).

## 0.2.0 - 2022-05-04

* Real start of development!
* Implement pseudo-CI behavior
* Add job to set persistent environment variables on Windows
* Add job to download profiles from a public remote git repository
* Complete CI to automatically build and publish executable for Ubuntu LTS and Windows
* Upgrade every dependencies

> See the [GitHub Release for a detailed changelog](https://github.com/Guts/qgis-deployment-cli/releases/tag/0.2.0).

## 0.1.0 - 2021-05-20

* First version, really minimalist

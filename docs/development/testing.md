# Tests

The project aims to be fully tested on every targetted platform through intensive CI/CD on every Pull Request.

Still, it's preferable to run tests locally before pushing to the public remote repository.

## Structure

- tests are located in the `tests` subfolder
- a test file is prefixed with `test_`
- ideally a test is written using the standard library, so as a "pure" unittest class, even if for some needs the pytest framework can be used.
- quick tests scripts can be stored in `tests/dev` folder to illustrate or check a behavior

## Requirements

To run the tests, you need to install development requirements ([Ubuntu](./ubuntu.md#develop-on-ubuntu) or [Windows](./windows.md#develop-on-windows)).

Complete it by installing tests requirements:

```sh
python -m pip install -U -e .[test]
```

## Run unit tests

Simply run Pytest:

```sh
pytest
```

It's also possible to run an individual test:

```sh
python -m unittest tests.test_qplugin_object.TestQgisPluginObject.test_profile_load_from_json_basic
```

## Try current QDT version

Let's say you're working on a branch and you want to run QDT against your changes.
Make the following changes to the `scenario.qdt.yml` to point to the current folder:

```yaml
[...]
steps:
  - name: Download profiles from remote git repository
    uses: qprofiles-downloader
    with:
      source: file://.
      protocol: git_local
[...]
```

Every time you edit the profiles stored in the `examples` folder, don't forget to commit to your local history:

```sh
git commit examples/ -m "wip"
QGIS_CUSTOM_CONFIG_PATH=tests/fixtures/tmp/ qdt -vv -s scenario.qdt.yml
# On Windows PowerShell
# $env:QGIS_CUSTOM_CONFIG_PATH="tests/fixtures/tmp/"; qdt -vv -s .\scenario.qdt.yml
```

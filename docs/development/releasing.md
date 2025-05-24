# Release workflow

1. Fill the `CHANGELOG.md` with the new version. You can write it manually or use the auto-generated release notes by Github:
    1. Go to [project's releases](https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/releases) and click on `Draft a new release`
    1. In `Choose a tag`, enter the new tag (obviously complying with [SemVer](https://semver.org/))
    1. Click on `Generate release notes`
    1. Copy/paste the generated text from `## What's changed` until the line before `**Full changelog**:...` in the CHANGELOG.md replacing `What's changed` with the tag and the publication date
1. Commit changes with a message like `release: bump version to X.x.x` to the main branch
1. Apply a git tag with the relevant version: `git tag -a 0.3.0 {git commit hash} -m "New awesome feature"`
1. Push commit and tag to main branch: `git push --tags`

If things go wrong (failed CI/CD pipeline, missed step...), here comes the fix process:

```sh
git tag -d old
git push origin :refs/tags/old
git push --tags
```

And try again!

----

## Manual upload to PyPi

> This method requires an API token on PyPi

If the CI/CD fails for any reason, here comes the manual procedure:

1. Install required packages:

    ```sh
    python -m pip install -U build setuptools-scm twine wheel
    ```

1. Install package in editable mode:

    ```sh
    python -m pip install -e .
    ```

1. Clean previous builds and build package artifacts:

    ```sh
    rm -rf dist/
    python -m build --no-isolation --sdist --wheel --outdir dist/ .
    ```

1. Upload built artifacts to PyPi:

    ```sh
    twine upload -u __token__ dist/*
    ```

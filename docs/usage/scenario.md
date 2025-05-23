# Write your deployment scenario

## What is a scenario?

This is the main way to use QDT. You write your deployment scenario by describing the steps to be done to prepare the QGIS environment, take a coffee (cup of tea is also tolerated) and look at the scenario running.

In concrete terms, a scenario is a [YAML file](https://fr.wikipedia.org/wiki/YAML) whose extension (`.yaml` or `.yml`) can be suffixed with `.qdt` so as to be more easily distinguished by the tool in the midst of potential other YAML files. Example: `scenario.qdt.yml`. The syntax is largely inspired by DevOPS oriented tools like Ansible or CI/CD platforms (GitHub Actions, GitLab CI in particular).

A scenario has 3 sections:

- `metadata`: to describe the scenario (title, description, etc.)
- `settings`: to set execution parameters to be applied to QDT, in the form of keys/values
- `steps`: the steps that the deployment scenario will successively take. Each step can call for a "job".

By default, QDT looks for a file named `scenario.qdt.yml` in the current directory.  
If it is not found, it will expect subcommands to run.

### Jobs

A *job* is a logical module that is called by a *step* in a *scenario*, by passing it parameters. Concretely, each job is a Python module of QDT ([here in the code](https://qgis-deployment.github.io/qgis-deployment-toolbelt-cli/_apidoc/qgis_deployment_toolbelt.jobs.html)).

A step consists of 3 elements:

- `name`: the name of the step
- `uses` : the job identifier to use
- `with` : the parameters to pass to the Job

```{button-link} ../jobs/index.html
:color: primary
:shadow:
:expand:

See available jobs
```

:::{tip}
Editing a scenario file can be tricky and since it's a critical piece of the QDT workflow, the project provide some tooling to help writing and checking them: [How to automatically validate QDT files](../guides/howto_validate_profiles_scenarios.md).
:::

----

## Sample scenario

For development and test purposes, project provides a [sample scenario](https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/blob/main/tests/fixtures/scenarios/good_scenario_sample.qdt.yml):

```{eval-rst}
.. literalinclude:: ../../tests/fixtures/scenarios/good_scenario_sample.qdt.yml
  :language: yaml
```

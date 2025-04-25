# Shortcuts manager

Use this job to set the default profile in profiles.ini file.

----

## Use it

Sample job configuration in your scenario file:

```yaml
- name: Set default profile to conf_qgis_fr
    uses: default-profile-setter
    with:
      profile: conf_qgis_fr
```

----

## Options

### profile

Name of the profile to set as default profile.

----

## Schema

```{eval-rst}
.. literalinclude:: ../schemas/scenario/jobs/default-profile-setter.json
  :language: json
```

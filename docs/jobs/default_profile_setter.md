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
      force_profile_selection_policy: true
```

----

## Options

### profile

Name of the profile to set as default profile.

### force_profile_selection_policy

Force the setting `selectionpolicy` to 1, which will always open the profile defined in the `defaultprofile` key in profile.ini file. In this context, this job will force QGIS to always start with the profile specified in this job.

----

## Schema

```{eval-rst}
.. literalinclude:: ../schemas/scenario/jobs/default-profile-setter.json
  :language: json
```

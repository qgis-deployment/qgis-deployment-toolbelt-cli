# Default profile setter

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

Force the key `selectionPolicy` to 1, which will always open the profile defined in the `defaultProfile` key in `profiles.ini` file. In this context, this job will force QGIS to always start with the profile specified in this job.
It's the same behavior as [the option _Always use profile_ in QGIS user profiles preferences](https://docs.qgis.org/latest/en/docs/user_manual/introduction/qgis_configuration.html#setting-user-profile).

----

## Schema

```{eval-rst}
.. literalinclude:: ../schemas/scenario/jobs/default-profile-setter.json
  :language: json
```

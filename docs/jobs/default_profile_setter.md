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
      force_profile_selection_policy: 1
```

----

## Options

### profile

Name of the profile to set as default profile.

### force_profile_selection_policy

:::{caution}
This option's behavior changed with version 0.40.0. Before it was just a boolean (see [old version of this page](https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/blob/b878f3c124350c6b29cf3b1f27943720fdf3dccd/docs/jobs/default_profile_setter.md?plain=1#L27-L30)).
Make sure the new behavior is consistent with what you expect from this option.
:::

Force the key `selectionPolicy` to the desired value in `profiles.ini`:

* `0`: Use last closed profile (default behavior). In out context, `profile` value may be overridden later by the user.
* `1`: Always open a specific profile. In our context, it will always open the default profile configured for this task.
* `2`: Choose at startup. In our context, the `profile` value will never be used.

See [QGIS user profiles documentation](https://docs.qgis.org/latest/en/docs/user_manual/introduction/qgis_configuration.html#setting-user-profile) for further details.

----

## Schema

```{eval-rst}
.. literalinclude:: ../schemas/scenario/jobs/default-profile-setter.json
  :language: json
```

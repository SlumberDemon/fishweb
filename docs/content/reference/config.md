# App Config

An apps configurations are defined in a `fishweb.yaml` file.

Here is an example config:

```yaml
app_type: asgi
entry: main:app
venv_path: .venv
reload: false
crons:
  - id: "my-cron"
    interval: "0/15 * * * *"
```

## Fields

### `app_type`

This field defines the type of app, by default this is `asgi`. To learn more about app types see [app anatomy](/content/concepts/anatomy).

```yaml
app_type: asgi | static
```

### `entry`

The ASGI import path `mypkg.myfile:application`. Defaults to `main:app`.

```yaml
entry: main:app
```

### `venv_path`

Path to the python virtual environment. Defaults to `.venv`.

```yaml
venv_path: .venv
```

### `reload`

Enables auto reloading for an app, if you make changes they will be reflected without needing to restart fishweb. This is disabled by default.

```yaml
reload: false | true
```

### `crons`

:::warning Notice
While this field can be provided, it currently has no proper implementation; please don't use it.
:::

The cron `id` should not have any spaces. The `interval` is a [cron expression](https://cron-checker.com/).

```yaml
crons:
  - id: "my-cron"
    interval: "0/15 * * * *"
```

# App Config

Per-app configuration is defined in a `fishweb.yaml` file.

For example:

```yaml
app_type: process
run_cmd: "uv run uvicorn main:app --port 9999"
port: 9999
reload: false
```

## Fields

### `type`

This field defines the type of app.
Defaults to `static`.
Possible values are `process` and `static`.

To learn more about app types see [Process Apps](/content/concepts/process) and [Static Apps](/content/concepts/static).

```yaml
type: process | static
```

### `run`

The command that runs the app. If you want fishweb to generate the port use $PORT.

```yaml
run: "uv run uvicorn main:app --port $PORT"
```

### `port`

Useful for languages/frameworks that don't allow for port flag or for always using the same port.
May cause issues if the port isn't avalible.

```yaml
port: 9999
```

### `reload`

Enables live reloading for an app, if you make changes they will be reflected without needing to restart Fishweb.
This is disabled by default.
Has no effect on static apps.

```yaml
reload: false | true
```

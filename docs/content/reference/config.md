# App Config

Per-app configuration is defined in a `fishweb.yaml` file.

For example:

```yaml
app_type: asgi
entry: main:app
venv_path: .venv
reload: false
```

## Fields

### `app_type`

This field defines the type of app.  
Defaults to `asgi`.  
Possible values are `asgi`, `wsgi`, and `static`.

To learn more about app types see [ASGI Apps](/content/concepts/asgi), [WSGI Apps](/content/concepts/wsgi), and [Static Apps](/content/concepts/static).

```yaml
app_type: asgi
```

### `entry`

The import path of your app callable, for example `mypkg.myfile:myapp`.  
Defaults to `main:app`.  
Has no effect on static apps.

```yaml
entry: main:app
```

### `venv_path`

Path to the Python virtual environment for your app, relative to its directory.  
Defaults to `.venv`.  
Has no effect on static apps.

```yaml
venv_path: .venv
```

### `reload`

Enables live reloading for an app, if you make changes they will be reflected without needing to restart Fishweb.  
This is disabled by default.  
Has no effect on static apps.

```yaml
reload: false | true
```

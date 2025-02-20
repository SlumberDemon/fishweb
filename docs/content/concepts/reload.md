# Live Reloading

When developing a Python app, enabling live reloading will allow changes to the app's folder on disk to be reflected in real-time without needing to restart Fishweb.
This can be enabled either via a [command-line option](/content/reference/cli#options-1) for all apps or per-app in the [config](/content/reference/config#reload) file.

::: code-group

```sh [CLI]
fishweb serve --reload
```

```yaml [fishweb.yaml]
reload: true
```

:::

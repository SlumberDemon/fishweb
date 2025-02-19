# Live editing

When developing a python app, enabling `reload` will allow for live updates without the need to restart fishweb for every change.
This can be enabled either via a [flag](/content/reference/cli#options-1) for all apps or a specific one with the [config](/content/reference/config#reload).

CLI
```sh
fishweb serve --reload
```

fishweb.yaml
```yaml
reload: true
```

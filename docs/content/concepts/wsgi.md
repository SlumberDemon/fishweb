# WSGI Apps

[WSGI](https://asgi.readthedocs.io/en/latest/introduction.html#wsgi-compatibility) apps work much the same way as ASGI apps in Fishweb.
You only need to do two things to enable support for them:

1. Install Fishweb with the `wsgi` extra, e.g. `uv tool install fishweb[wsgi]`
2. Set the [`app_type`](/content/reference/config#app-type) in your app's config file to `wsgi`

::: code-group

```yaml [fishweb.yaml]
app_type: wsgi
```

:::

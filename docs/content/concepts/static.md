# Static App

You can also make simple HTML apps without python. These can be edited on the fly without the need for `reload`.
The main file in a static app is `index.html`. If you want to handle 404 error you can add `404.html`.
As fishweb looks for ASGI apps by default, static apps need a config file with the required configurations.

::: code-group

```html [index.html]
<!DOCTYPE html>
<html lang="en">
    <head>
        <title>Fishweb</title>
    </head>
    <body>
        <h1>Hello from fishweb</h1>
    </body>
</html>
```

```yaml [fishweb.yaml]
app_type: static
```

:::

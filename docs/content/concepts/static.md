# Static Apps

You can also make static HTML/CSS/JS apps without Python.
These can be updated and will reflect changes on the fly without the need for [live reloading](/content/concepts/reload).

The main file in a static app is `index.html`.
If you want to handle 404 Not Found errors you can add a `404.html` file.
Most of the heavy lifting is done by Starlette's [StaticFiles](https://www.starlette.io/staticfiles/) middleware.

As static apps are the default you can make a minimal setup that does not require a config file.

> [!INFO]
> Static apps **do not** support crons

::: code-group

```html [index.html]
<!DOCTYPE html>
<html lang="en">
    <head>
        <title>Fishweb Static App</title>
    </head>
    <body>
        <h1>Hello from Fishweb</h1>
    </body>
</html>
```

```yaml [fishweb.yaml]
app_type: static
```

:::

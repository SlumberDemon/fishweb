# Virtual Environments

To run a Python app with a framework or additional libraries you need a virtual environment with those dependencies installed.

The default virtual environment path Fishweb will check is `.venv`, relative to your app's directory.
This can be changed in the [config](/content/reference/config#venv-path) file.

> [!IMPORTANT]
> The version of Python used in the virtual environment **must match** the version you are using to run Fishweb.

## How it works

When loading your app, Fishweb will temporarily add the virtual environment to the Python `sys.path` list, so that your app can access it during start-up.

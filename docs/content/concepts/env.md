# Environment Variables

Currently fishweb does not handle the loading of `.env` files. This is a feature that is planned for future releases, see [issue #20](https://github.com/SlumberDemon/fishweb/issues/20).

## Fishweb Environment Variables

Fishweb automatically adds the following environment variables:

- `FISHWEB_APP_NAME`: The name of the application.
- `FISHWEB_DATA_DIR`: The directory where fishweb apps can store their data. Also to allow for arowana compatibility.
- `FISHWEB_VERSION`: The version of fishweb.

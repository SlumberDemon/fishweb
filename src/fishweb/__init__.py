from fishweb.app import DEFAULT_ROOT_DIR, create_fishweb_app

app = create_fishweb_app(
    bind_address="localhost:8888",  # TODO: get it from uvicorn?
    root_dir=DEFAULT_ROOT_DIR,  # TODO: get it from argv?
)

__all__ = ("app",)

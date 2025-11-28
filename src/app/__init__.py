import uvicorn

APP_NAME = "app.core.app:app"


def start() -> None:
    """CLI entrypoint used by `uv run start` to launch the FastAPI app."""
    uvicorn.run(APP_NAME, host="0.0.0.0", port=8000, reload=True)

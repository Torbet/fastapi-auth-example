import uvicorn

APP_NAME = "app.core.app:app"


def start() -> None:
    uvicorn.run(APP_NAME, host="0.0.0.0", port=8000, reload=True)

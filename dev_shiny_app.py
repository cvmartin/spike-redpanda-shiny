"""Launch the application as defined in src/app, in local container."""

from app.run import run_app

run_app(options={"port": 8000, "launch_browser": False})  # noqa: S104

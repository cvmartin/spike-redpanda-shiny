"""Launch the application as defined in src/app, inside container."""

from app.run import run_app

run_app(options={"host": "0.0.0.0", "port": 3838})  # noqa: S104

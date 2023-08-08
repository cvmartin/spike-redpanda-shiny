"""Launch the application as defined in src/app, in local container."""

from app.config import config_external_dev
from app.run import run_app

run_app(
    options={"port": 8000, "launch_browser": False},
    config_external=config_external_dev,
)

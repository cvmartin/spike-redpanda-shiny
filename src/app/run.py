"""Run shiny application."""
from typing import Union

from shiny import App

from app.app_server import app_server
from app.app_ui import app_ui
from app.config import ConfigExternal


def run_app(
    options: dict[str, Union[bool, int, float, str]],
    config_external: ConfigExternal,
) -> None:
    """Launch application.

    Args:
        options (dict[str, Union[bool, int, float, str]]): Options passed onto shiny `app.run`
        config_external (ConfigExternal): External configuration to pass onto the application.
    """
    app = App(app_ui, app_server)

    app.starlette_app.state.CONFIG_EXTERNAL = config_external

    # run application with arbitrary shiny arguments
    app.run(**options)

"""Run shiny application."""
from typing import Union

from shiny import App

from app.app_server import app_server
from app.app_ui import app_ui


def run_app(options: dict[str, Union[bool, int, float, str]]) -> None:
    """Launch application.

    Args:
        options (dict[str, Union[bool, int, float, str]]): Options passed onto shiny `app.run`
    """
    app = App(app_ui, app_server)

    # run application with arbitrary shiny arguments
    app.run(**options)

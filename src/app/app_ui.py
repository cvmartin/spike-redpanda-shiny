"""UI side of application."""

from shiny import ui

app_ui = ui.page_fluid(
    "This should update automatically",
    ui.output_text_verbatim("async_text"),
)

"""UI side of application."""

from shiny import ui

app_ui = ui.page_fluid(
    "Meter measurements",
    ui.output_text_verbatim("text_meter_measurements"),
    "Average measurements over 10 seconds",
    ui.output_text_verbatim("text_avg_meter_values"),
)

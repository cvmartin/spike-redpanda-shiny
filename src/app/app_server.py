"""Server side of application."""
from shiny import Inputs, Outputs, Session, render, ui


def app_server(
    input: Inputs,  # noqa: A002
    output: Outputs,
    session: Session,  # noqa: ARG001
) -> None:
    @output(id="txt")
    @render.text
    def _():
        return f"n*2 is {input.n() * 2}"

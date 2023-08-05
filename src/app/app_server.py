"""Server side of application."""
from typing import Callable

from app.config import KafkaConsumerConfig
from app.helpers.kafka import KafkaMessage, rval_from_kafka_topic
from shiny import Inputs, Outputs, Session, reactive, render

REDPANDA_SERVERS = "localhost:9092"


def app_server(
    input: Inputs,  # noqa: A002
    output: Outputs,
    session: Session,  # noqa: ARG001
) -> None:
    # App setup
    kafka_consumer_config = KafkaConsumerConfig(bootstrap_servers=REDPANDA_SERVERS)

    @reactive.Calc
    def meter_measurements() -> Callable[[], KafkaMessage]:
        return rval_from_kafka_topic(
            "meter_measurements",
            kafka_consumer_config=kafka_consumer_config,
        )

    @reactive.Calc
    def avg_meter_values() -> Callable[[], KafkaMessage]:
        return rval_from_kafka_topic(
            "avg_meter_values",
            kafka_consumer_config=kafka_consumer_config,
        )

    # App output
    @output(id="text_meter_measurements")
    @render.text
    def _():
        return str(meter_measurements()())

    @output(id="text_avg_meter_values")
    @render.text
    def _():
        return str(avg_meter_values()())

"""Server side of application."""
from typing import Callable

from confluent_kafka.schema_registry import SchemaRegistryClient
from shiny import Inputs, Outputs, Session, reactive, render

from app.config import ConfigExternal, KafkaConsumerConfig
from app.helpers.kafka import KafkaMessage, rval_from_kafka_topic
from data_producer.avro_parser import AvroParser


# ruff: noqa: ARG001, A002
def app_server(
    input: Inputs,
    output: Outputs,
    session: Session,
) -> None:
    """Server side of application.

    Args:
        input (Inputs): Shiny object.
        output (Outputs): Shiny object.
        session (Session): Shiny object.
    """
    # App setup
    app_state = session.app.starlette_app.state
    config_external: ConfigExternal = app_state.CONFIG_EXTERNAL

    meter_measurements_parser = AvroParser(
        schema_registry_client=SchemaRegistryClient(
            conf={"url": config_external.schema_registry_url},
        ),
        schema_subject="meter_measurements-value",
        schema_version=1,
        topic_name="meter_measurements",
    )

    kafka_consumer_config = KafkaConsumerConfig(
        bootstrap_servers=config_external.bootstrap_servers,
        value_deserializer=meter_measurements_parser.deserialize_value,
    )

    @reactive.Calc
    def val_meter_measurements() -> Callable[[], KafkaMessage]:
        kafka_topic = "meter_measurements"

        return rval_from_kafka_topic(
            kafka_topic,
            kafka_consumer_config=kafka_consumer_config,
        )

    @reactive.Calc
    def val_avg_meter_values() -> Callable[[], KafkaMessage]:
        return rval_from_kafka_topic(
            "avg_meter_values",
            kafka_consumer_config=kafka_consumer_config,
        )

    @reactive.Calc
    def accu_meter_measurements() -> Callable[[], list[KafkaMessage]]:
        rv_state: reactive.Value[list[KafkaMessage]] = reactive.Value([])

        @reactive.Effect
        @reactive.event(val_meter_measurements())
        def _() -> None:
            state = rv_state.get()
            # copy on assignment to handle mutability
            # https://shiny.posit.co/py/docs/reactive-mutable.html#copy-on-assignment
            copy_state = state.copy()
            copy_state.append(val_meter_measurements()())
            rv_state.set(copy_state)

        return rv_state

    # App output
    @output(id="text_meter_measurements")
    @render.text
    def _() -> str:
        return str(val_meter_measurements()())

    @output(id="text_avg_meter_values")
    @render.text
    def _() -> str:
        return str(val_avg_meter_values()())

    @output(id="text_total_accu_meter_measurements")
    @render.text
    def _() -> str:
        return f"Total messages: {len(accu_meter_measurements()())}"

    @output(id="text_accu_meter_measurements")
    @render.text
    def _() -> str:
        # new line after comma.
        return str(accu_meter_measurements()()).replace("}, ", "},\n")

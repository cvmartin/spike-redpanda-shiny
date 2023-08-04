"""Server side of application."""
import asyncio
import json
from typing import Any, AsyncGenerator, Callable

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from shiny import Inputs, Outputs, Session, reactive, render

KafkaMessage = dict[str, Any]


async def consume_kafka_topic(
    topic_name: str,
    bootstrap_servers: str,
) -> AsyncGenerator[str, None]:
    """Consume asynchronously from a kafka topic."""
    consumer = AIOKafkaConsumer(
        topic_name,
        bootstrap_servers=bootstrap_servers,
    )

    await consumer.start()

    try:
        message: ConsumerRecord[bytes, bytes]
        async for message in consumer:
            yield message.value.decode("utf-8")
    finally:
        await consumer.stop()


async def watch_kafka_topic(
    topic_name: str,
    update_variable: reactive.Value[KafkaMessage],
) -> None:
    async for message in consume_kafka_topic(
        topic_name=topic_name,
        bootstrap_servers="localhost:9092",
    ):
        update_variable.set(json.loads(message))
        await reactive.flush()


def app_server(
    input: Inputs,  # noqa: A002
    output: Outputs,
    session: Session,  # noqa: ARG001
) -> None:
    # App setup

    @reactive.Calc
    def meter_measurements() -> Callable[[], KafkaMessage]:
        reactive_val = reactive.Value({})
        _ = (
            asyncio.create_task(
                watch_kafka_topic(
                    topic_name="meter_measurements",
                    update_variable=reactive_val,
                ),
            ),
        )
        return reactive_val

    @reactive.Calc
    def avg_meter_values() -> Callable[[], KafkaMessage]:
        reactive_val = reactive.Value({})
        _ = (
            asyncio.create_task(
                watch_kafka_topic(
                    topic_name="avg_meter_values",
                    update_variable=reactive_val,
                ),
            ),
        )
        return reactive_val

    # App output
    @output(id="text_meter_measurements")
    @render.text
    def _():
        return str(meter_measurements()())

    @output(id="text_avg_meter_values")
    @render.text
    def _():
        return str(avg_meter_values()())

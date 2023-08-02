"""Server side of application."""
import asyncio
import json
from typing import Any, AsyncGenerator

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
        loop=asyncio.get_event_loop(),
        bootstrap_servers=bootstrap_servers,
    )

    await consumer.start()

    try:
        message: ConsumerRecord[bytes, bytes]
        async for message in consumer:
            yield message.value.decode("utf-8")
    finally:
        await consumer.stop()


async def watch_changes(topic_name: str, rval: reactive.Value[KafkaMessage]) -> None:
    async for message in consume_kafka_topic(
        topic_name=topic_name, bootstrap_servers="localhost:9092"
    ):
        rval.set(json.loads(message))
        await reactive.flush()


def app_server(
    input: Inputs,  # noqa: A002
    output: Outputs,
    session: Session,  # noqa: ARG001
) -> None:
    # App setup
    meter_measurements_val = reactive.Value({})
    avg_meter_values_val = reactive.Value({})

    # following https://beta.ruff.rs/docs/rules/asyncio-dangling-task/
    background_tasks: set[asyncio.Task] = set()
    background_tasks.add(
        asyncio.create_task(
            watch_changes(topic_name="meter_measurements", rval=meter_measurements_val),
        ),
    )
    background_tasks.add(
        asyncio.create_task(
            watch_changes(topic_name="avg_meter_values", rval=avg_meter_values_val),
        ),
    )

    # App output
    @output(id="text_meter_measurements")
    @render.text
    def _():
        return str(meter_measurements_val.get())

    @output(id="text_avg_meter_values")
    @render.text
    def _():
        return str(avg_meter_values_val.get())

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


async def watch_changes(rval: reactive.Value[KafkaMessage]) -> None:
    async for message in consume_kafka_topic(
        topic_name="meter_measurements", bootstrap_servers="localhost:9092"
    ):
        rval.set(json.loads(message))
        await reactive.flush()


def app_server(
    input: Inputs,  # noqa: A002
    output: Outputs,
    session: Session,  # noqa: ARG001
) -> None:
    # App setup
    incoming_val = reactive.Value({})

    # following https://beta.ruff.rs/docs/rules/asyncio-dangling-task/
    background_tasks = set()
    task = asyncio.create_task(watch_changes(incoming_val))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    # App output
    @output(id="async_text")
    @render.text
    def _():
        return str(incoming_val.get())

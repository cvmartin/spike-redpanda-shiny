"""Kafka utilities for shiny application."""
import asyncio
import json
from typing import Any, AsyncGenerator, Callable

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from app.config import KafkaConsumerConfig
from shiny import reactive

KafkaMessage = dict[str, Any]


async def consume_kafka_topic(
    topic_name: str,
    kafka_consumer_config: KafkaConsumerConfig,
) -> AsyncGenerator[str, None]:
    """Consume kafka topic asynchronously.

    Args:
        topic_name (str): Kafka topic
        kafka_consumer_config (KafkaConsumerConfig): Kafka consumer configuration.

    Returns:
        AsyncGenerator[str, None]: An asynchronous generator that yields Kafka messages as they arrive on the topic.

    Yields:
        str: A decoded message from the Kafka topic as a string.
    """
    consumer = AIOKafkaConsumer(
        topic_name,
        bootstrap_servers=kafka_consumer_config.bootstrap_servers,
        # setting to "earliest" fetches all the messages.
        auto_offset_reset="latest",
    )

    await consumer.start()

    try:
        message: ConsumerRecord[bytes, bytes]
        async for message in consumer:
            yield message.value.decode("utf-8")
    finally:
        await consumer.stop()


async def update_rval_from_kafka_topic(
    topic_name: str,
    update_variable: reactive.Value[KafkaMessage],
    kafka_consumer_config: KafkaConsumerConfig,
) -> None:
    """Change a reactive.Value on a new message in Kafka topic.

    Args:
        topic_name (str): Kafka topic
        update_variable (reactive.Value[KafkaMessage]): Value which will be updated on a new message.
        kafka_consumer_config (KafkaConsumerConfig): Kafka consumer configuration.
    """
    async for message in consume_kafka_topic(
        topic_name=topic_name,
        kafka_consumer_config=kafka_consumer_config,
    ):
        update_variable.set(json.loads(message))
        await reactive.flush()


def rval_from_kafka_topic(
    topic_name: str,
    kafka_consumer_config: KafkaConsumerConfig,
) -> Callable[[], KafkaMessage]:
    """Create asynchronous task to consume from kafka topic.

    And returns a reactive value with the changes.

    Args:
        topic_name (str): Kafka topic.
        kafka_consumer_config (KafkaConsumerConfig): Kafka consumer configuration.

    Returns:
        Callable[[], KafkaMessage]: reactive value.
    """
    reactive_val: reactive.Value[KafkaMessage] = reactive.Value()
    _ = (
        asyncio.create_task(
            update_rval_from_kafka_topic(
                topic_name=topic_name,
                update_variable=reactive_val,
                kafka_consumer_config=kafka_consumer_config,
            ),
        ),
    )
    return reactive_val

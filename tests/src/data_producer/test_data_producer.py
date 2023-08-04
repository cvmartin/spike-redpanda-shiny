import asyncio
import datetime
from typing import Any, AsyncGenerator, Generator

import pytest
import pytest_asyncio
from aiokafka import AIOKafkaProducer
from data_producer.data_producer import (
    MessageMeterMeasurement,
    produce_data_messages_once,
)
from helpers.container.redpanda import RedpandaContainer
from kafka import KafkaConsumer, TopicPartition
from kafka.consumer.fetcher import ConsumerRecord

TOPIC = "foo_topic"
REDPANDA_SERVERS = "localhost:9092"
METER_IDS = ["X", "Y", "Z"]


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, Any, Any]:
    """Overrides pytest default function scoped event loop."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def async_kafka_producer() -> AsyncGenerator[AIOKafkaProducer, Any]:
    """Provides an asynchronous kafka producer ready to use."""
    producer = AIOKafkaProducer(
        bootstrap_servers=REDPANDA_SERVERS,
    )
    await producer.start()
    yield producer
    await producer.stop()


def kafka_topic_poll_all_messages(topic: str, bootstrap_servers: str) -> list[str]:
    """Retrieves all messages in a topic.

    It assumes the messages are encoded using `utf-8`.

    Args:
        topic (str): Kafka topic
        bootstrap_servers (str): Kafka servers.

    Returns:
        list[str]: List of decoded messages values.
    """
    consumer = KafkaConsumer(bootstrap_servers=bootstrap_servers)
    tp = TopicPartition(topic, 0)
    consumer.assign([tp])
    # seek_to_beginning() and poll() must follow
    # to fetch all messages.
    consumer.seek_to_beginning()
    msgs: list[ConsumerRecord] = consumer.poll(timeout_ms=100)[tp]
    consumer.close()
    return [x.value.decode("utf-8") for x in msgs]


class TestMessageMeterMeasurement:
    def test_to_from_json(self):
        message_initial = MessageMeterMeasurement(
            meter_id="test_id",
            measurement=42,
            event_timestamp=datetime.datetime.now(tz=datetime.timezone.utc).timestamp(),
        )

        message_reconstructed = MessageMeterMeasurement.from_json(
            json_string=message_initial.to_json(),
        )

        assert message_initial == message_reconstructed


class TestProduceDataMessagesOnce:
    @pytest.mark.asyncio()
    async def test_produce_and_consume(
        self,
        async_kafka_producer: AIOKafkaProducer,
    ) -> None:
        await produce_data_messages_once(
            producer=async_kafka_producer,
            topic=TOPIC,
            meter_ids=METER_IDS,
        )

        messages = kafka_topic_poll_all_messages(
            topic=TOPIC, bootstrap_servers=REDPANDA_SERVERS
        )

        assert len(messages) > 0

"""Produce random data. Intended to be run inside a docker container."""

import asyncio
import datetime
import logging
import random
from dataclasses import dataclass
from venv import logger

import orjson
from aiokafka import AIOKafkaProducer

logging.basicConfig(level=logging.INFO)

METER_IDS = ["A", "B", "C", "D", "E"]
KAFKA_TOPIC = "meter_measurements"


@dataclass
class KafkaProducerConfig:
    """Generic configuration for kafka producer."""

    redpanda_brokers: str


@dataclass
class MessageMeterMeasurement:
    """Generic message to be produced to Kafka brokers."""

    meter_id: str
    measurement: float
    event_timestamp: float

    def to_json(self) -> bytes:
        """Convert to json.

        Note the use of `orjson` to convert datetimes to strings.

        Returns:
            str: dataclass as json object
        """
        return orjson.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_string: bytes) -> "MessageMeterMeasurement":
        """Reconstructs class from an string that can be parsed to json.

        Args:
            json_string (str): string parsable to json.

        Returns:
            MessageMeterMeasurements: class, reconstructed.
        """
        loaded_data = orjson.loads(json_string)
        return cls(
            meter_id=loaded_data["meter_id"],
            measurement=loaded_data["measurement"],
            event_timestamp=loaded_data["event_timestamp"],
        )


async def custom_produce_kafka_messages(
    kafka_producer_config: KafkaProducerConfig,
) -> None:
    """Custom kafka producer.

    Generates 5 entries every two seconds.

    Args:
        kafka_producer_config (KafkaProducerConfig): Kafka configuration.
    """
    producer = AIOKafkaProducer(
        bootstrap_servers=kafka_producer_config.redpanda_brokers,
    )
    await producer.start()
    try:
        while True:
            message_topic: str = KAFKA_TOPIC
            for x in METER_IDS:
                message_value: bytes = MessageMeterMeasurement(
                    meter_id=x,
                    measurement=random.randint(0, 100),  # noqa: S311
                    event_timestamp=datetime.datetime.now(
                        tz=datetime.timezone.utc,
                    ).timestamp(),
                ).to_json()
                try:
                    await producer.send(message_topic, value=message_value)

                except Exception:  # noqa: PERF203
                    logger.error(
                        "Error sending message",
                        extra={"topic": message_topic, "value": message_value},
                    )
            await asyncio.sleep(2)
    finally:
        await producer.stop()


def run_producer(kafka_producer_config: KafkaProducerConfig) -> None:
    """Run kafka producer in an async loop.

    Args:
        kafka_producer_config (KafkaProducerConfig): Kafka configuration.
    """
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            custom_produce_kafka_messages(kafka_producer_config=kafka_producer_config)
        )
    finally:
        loop.close()

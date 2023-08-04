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


@dataclass
class KafkaDataProducerConfig:
    """Generic configuration for kafka producer."""

    redpanda_brokers: str
    kafka_topic: str
    meter_ids: list[str]


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


async def produce_data_messages_once(
    producer: AIOKafkaProducer,
    topic: str,
    meter_ids: list[str],
) -> None:
    """Produce custom data.

    One message per element in `meter_ids`.

    Args:
        producer (AIOKafkaProducer): Kafka producer.
        topic (str): Kafka topic
        meter_ids (list[str]): List of meter IDs to iterate over.
    """
    message_topic: str = topic
    for x in meter_ids:
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
        finally:
            await producer.flush()


async def produce_data_messages_loop(
    kafka_producer_config: KafkaDataProducerConfig,
) -> None:
    """Produce data in an infinite loop.

    Frequency of data broadcasting is defined here.

    Args:
        kafka_producer_config (KafkaProducerConfig): Kafka configuration.
    """
    producer = AIOKafkaProducer(
        bootstrap_servers=kafka_producer_config.redpanda_brokers,
    )
    await producer.start()

    try:
        while True:
            await produce_data_messages_once(
                producer=producer,
                topic=kafka_producer_config.kafka_topic,
                meter_ids=kafka_producer_config.meter_ids,
            )
            await asyncio.sleep(2)
    finally:
        await producer.stop()

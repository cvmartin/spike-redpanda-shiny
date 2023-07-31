"""Produce random data. Intended to be run inside a docker container."""

import json
import logging
import random
import time
from concurrent.futures import Future
from dataclasses import dataclass
from venv import logger

from kafka import KafkaProducer
from kafka.producer.future import FutureRecordMetadata

logging.basicConfig(level=logging.INFO)

METER_IDS = ["A", "B", "C", "D", "E"]
KAFKA_TOPIC = "meter_measurements"


@dataclass
class KafkaProducerConfig:
    """Generic configuration for kakfa producer."""

    redpanda_brokers: str


@dataclass
class MessageMeterMeasurements:
    """Generic message to be produced to Kafka brokers."""

    meter_id: str
    measurement: float

    def to_json(self) -> bytes:
        """Convert to json.

        Returns:
            str: dataclass as json object
        """
        return json.dumps(self.__dict__).encode("utf-8")


def run_producer(kafka_producer_config: KafkaProducerConfig) -> None:
    """Run data producer."""
    producer = KafkaProducer(bootstrap_servers=kafka_producer_config.redpanda_brokers)

    while True:
        message_topic: str = KAFKA_TOPIC

        for x in METER_IDS:
            message_value: bytes = MessageMeterMeasurements(
                meter_id=x,
                measurement=random.randint(0, 100),  # noqa: S311
            ).to_json()

            try:
                future: Future[FutureRecordMetadata] = producer.send(
                    topic=message_topic,
                    value=message_value,
                )
                _: FutureRecordMetadata = future.get(timeout=10)
            except Exception:  # noqa: PERF203
                logger.error(
                    "Error sending message",
                    extra={"topic": message_topic, "value": message_value},
                )

            producer.flush()

        logger.info("Sent batch of messages", extra={"topic": message_topic})

        time.sleep(2)


if __name__ == "__main__":
    run_producer(
        kafka_producer_config=KafkaProducerConfig(redpanda_brokers=REDPANDA_BROKERS)
    )

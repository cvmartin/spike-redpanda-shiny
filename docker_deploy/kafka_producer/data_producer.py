"""Produce random data. Intended to be run inside a docker container."""

import json
import logging
import random
import time
from dataclasses import dataclass
from venv import logger

from kafka import KafkaProducer

logging.basicConfig(level=logging.DEBUG)

METER_IDS = ["A", "B", "C", "D", "E"]
KAFKA_TOPIC = "meter_measurements"
REDPANDA_BROKERS = "redpanda-1:29092"


@dataclass
class KafkaProducerConfig:
    """Generic configuration for kakfa producer."""

    redpanda_brokers: str = REDPANDA_BROKERS


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


def main() -> None:
    """Rund data producer."""
    producer = KafkaProducer(bootstrap_servers=KafkaProducerConfig.redpanda_brokers)

    while True:
        for x in METER_IDS:
            message_topic: str = KAFKA_TOPIC
            message_value: bytes = MessageMeterMeasurements(
                meter_id=x,
                measurement=random.randint(0, 100),  # noqa: S311
            ).to_json()

            try:
                future = producer.send(
                    topic=message_topic,
                    value=message_value,
                )
                _ = future.get(timeout=10)
            except Exception:  # noqa: PERF203
                logger.error(
                    "Error sending message",
                    extra={"topic": message_topic, "value": message_value},
                )

            producer.flush()

        time.sleep(2)


if __name__ == "__main__":
    main()

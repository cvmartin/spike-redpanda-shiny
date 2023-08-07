"""Configuration for kafka producers, in dev and docker."""
from dataclasses import dataclass

REDPANDA_BROKERS_DEV = "localhost:9092"
REDPANDA_BROKERS_DOCKER = "redpanda-1:29092"

REGISTRY_BROKERS_DEV = "http://localhost:8081"
REGISTRY_BROKERS_DOCKER = "http://redpanda-1:8081"

METER_IDS = ["A", "B", "C", "D", "E"]
KAFKA_TOPIC = "meter_measurements"


@dataclass
class KafkaDataProducerConfig:
    """Generic configuration for kafka producer."""

    bootstrap_servers: str
    schema_registry_url: str
    schema_subject: str
    schema_version: int
    topic: str
    meter_ids: list[str]


producer_config_dev = KafkaDataProducerConfig(
    bootstrap_servers=REDPANDA_BROKERS_DEV,
    schema_registry_url=REGISTRY_BROKERS_DEV,
    schema_subject="meter_measurements-value",
    schema_version=1,
    topic=KAFKA_TOPIC,
    meter_ids=METER_IDS,
)

producer_config_docker = KafkaDataProducerConfig(
    bootstrap_servers=REDPANDA_BROKERS_DOCKER,
    schema_registry_url=REGISTRY_BROKERS_DOCKER,
    schema_subject="meter_measurements-value",
    schema_version=1,
    topic=KAFKA_TOPIC,
    meter_ids=METER_IDS,
)

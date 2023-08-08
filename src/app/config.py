"""Configuration for application."""

from dataclasses import dataclass
from typing import Callable

REDPANDA_BROKERS_DEV = "localhost:9092"
REDPANDA_BROKERS_DOCKER = "redpanda-1:29092"

REGISTRY_BROKERS_DEV = "http://localhost:8081"
REGISTRY_BROKERS_DOCKER = "http://redpanda-1:8081"


@dataclass
class KafkaConsumerConfig:
    """Options (other than topic) to be used by the kafka consumer."""

    bootstrap_servers: str
    value_deserializer: Callable


@dataclass
class ConfigExternal:
    """External configuration, mainly secrets."""

    bootstrap_servers: str
    schema_registry_url: str


config_external_dev = ConfigExternal(
    bootstrap_servers=REDPANDA_BROKERS_DEV,
    schema_registry_url=REGISTRY_BROKERS_DEV,
)

config_external_docker = ConfigExternal(
    bootstrap_servers=REDPANDA_BROKERS_DOCKER,
    schema_registry_url=REGISTRY_BROKERS_DOCKER,
)

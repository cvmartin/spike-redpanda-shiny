from dataclasses import dataclass


@dataclass
class KafkaConsumerConfig:
    """Options (other than topic) to be used by the kafka consumer."""

    bootstrap_servers: str

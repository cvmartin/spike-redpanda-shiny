"""Configuration for kafka producers, in dev and docker."""
from data_producer.data_producer import KafkaDataProducerConfig

REDPANDA_BROKERS_DEV = "localhost:9092"
REDPANDA_BROKERS_DOCKER = "redpanda-1:29092"
METER_IDS = ["A", "B", "C", "D", "E"]
KAFKA_TOPIC = "meter_measurements"

producer_config_dev = KafkaDataProducerConfig(
    redpanda_brokers=REDPANDA_BROKERS_DEV,
    kafka_topic=KAFKA_TOPIC,
    meter_ids=METER_IDS,
)

producer_config_docker = KafkaDataProducerConfig(
    redpanda_brokers=REDPANDA_BROKERS_DOCKER,
    kafka_topic=KAFKA_TOPIC,
    meter_ids=METER_IDS,
)

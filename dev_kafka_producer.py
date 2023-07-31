"""Launch data producer, in dev."""
from data_producer.data_producer import KafkaProducerConfig, run_producer

REDPANDA_BROKERS = "localhost:9092"

run_producer(
    kafka_producer_config=KafkaProducerConfig(redpanda_brokers=REDPANDA_BROKERS)
)

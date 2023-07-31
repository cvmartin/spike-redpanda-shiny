"""Launch data producer, inside docker."""
from data_producer.data_producer import KafkaProducerConfig, run_producer

REDPANDA_BROKERS = "redpanda-1:29092"

run_producer(
    kafka_producer_config=KafkaProducerConfig(redpanda_brokers=REDPANDA_BROKERS)
)

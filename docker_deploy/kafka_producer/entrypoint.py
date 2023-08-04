"""Launch data producer, inside docker."""
import asyncio

from data_producer.config import producer_config_docker
from data_producer.data_producer import produce_data_messages_loop

asyncio.run(
    produce_data_messages_loop(kafka_producer_config=producer_config_docker),
)

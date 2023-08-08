import datetime
import random
from typing import Any
from uuid import uuid4

import pytest
from confluent_kafka.schema_registry import (
    SchemaRegistryClient,
)
from kafka import KafkaConsumer, KafkaProducer, TopicPartition
from kafka.consumer.fetcher import ConsumerRecord

from data_producer.avro_parser import AvroParser


@pytest.mark.skip(reason="depends on locally deployed broker")
def test_provisional():
    address_registry = "http://localhost:8081"
    bootstrap_server = "localhost:9092"
    message_topic = "testing_schemas"

    test_parser = AvroParser(
        schema_registry_client=SchemaRegistryClient(conf={"url": address_registry}),
        schema_subject="meter_measurements-value",
        schema_version=1,
        topic_name=message_topic,
    )

    message_key: str = str(uuid4())

    message_value: dict[str, Any] = {
        "meter_id": "Z",
        "measurement": random.randint(0, 100),  # noqa: S311
        "event_timestamp": datetime.datetime.now(
            tz=datetime.timezone.utc,
        ),
    }

    producer = KafkaProducer(
        bootstrap_servers=[bootstrap_server],
        key_serializer=test_parser.serialize_key,
        value_serializer=test_parser.serialize_value,
    )

    producer.send(
        topic=message_topic,
        key=message_key,
        value=message_value,
    )
    producer.flush()

    consumer = KafkaConsumer(
        bootstrap_servers=[bootstrap_server],
        key_deserializer=test_parser.deserialize_key,
        value_deserializer=test_parser.deserialize_value,
    )

    tp = TopicPartition(message_topic, 0)
    consumer.assign([tp])
    # seek_to_beginning() and poll() must follow
    # to fetch all messages.
    consumer.seek_to_beginning()
    msgs: list[ConsumerRecord] = consumer.poll(timeout_ms=100)[tp]  # type: ignore
    consumer.close()
    out = [x for x in msgs]
    print(out)

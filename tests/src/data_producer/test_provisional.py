import datetime
import random
from typing import Any
from uuid import uuid4

import pytest
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
)
from kafka import KafkaProducer

from data_producer.data_producer import retrieve_schema_from_registry


@pytest.mark.skip(reason="depends on locally deployed broker")
def test_provisional():
    address_registry = "http://localhost:8081"
    bootstrap_server = "localhost:9092"

    schema_registry_client = SchemaRegistryClient(conf={"url": address_registry})

    avro_key_serializer = AvroSerializer(
        schema_registry_client=schema_registry_client,
        schema_str='{"type": "string"}',
    )

    avro_value_serializer = AvroSerializer(
        schema_registry_client=schema_registry_client,
        schema_str=retrieve_schema_from_registry(
            schema_registry_url=address_registry,
            subject="meter_measurements-value",
            version=1,
        ),
    )

    message_key = str(uuid4())

    message_value: dict[str, Any] = {
        "meter_id": "Z",
        "measurement": random.randint(0, 100),  # noqa: S311
        "event_timestamp": datetime.datetime.now(
            tz=datetime.timezone.utc,
        ),
    }

    producer = KafkaProducer(bootstrap_servers=[bootstrap_server])

    message_topic = "testing_schemas"

    producer.send(
        topic=message_topic,
        key=avro_key_serializer(
            message_key,
            SerializationContext(message_topic, MessageField.KEY),
        ),
        value=avro_value_serializer(
            message_value,
            SerializationContext(message_topic, MessageField.VALUE),
        ),
    )

    producer.flush()

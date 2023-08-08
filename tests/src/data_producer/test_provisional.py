import datetime
import random
from typing import Any
from uuid import uuid4

import pytest
from confluent_kafka.schema_registry import (
    RegisteredSchema,
    Schema,
    SchemaRegistryClient,
)
from confluent_kafka.schema_registry.avro import AvroDeserializer, AvroSerializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
)
from kafka import KafkaConsumer, KafkaProducer, TopicPartition
from kafka.consumer.fetcher import ConsumerRecord


class AvroParser:
    def __init__(
        self,
        schema_registry_client: SchemaRegistryClient,
        schema_subject: str,
        schema_version: int,
        topic_name: str,
    ) -> None:
        self.schema_registry_client = schema_registry_client
        self.schema_subject = schema_subject
        self.schema_version = schema_version
        self.topic_name = topic_name

        self.key_schema: str = '{"type": "string"}'

        self.registered_value_schema: RegisteredSchema = (
            self.schema_registry_client.get_version(
                self.schema_subject,
                self.schema_version,
            )
        )
        self.value_schema: Schema = self.registered_value_schema.schema.schema_str

        self.avro_key_serializer = AvroSerializer(
            conf={"auto.register.schemas": False},
            schema_registry_client=self.schema_registry_client,
            schema_str=self.key_schema,
        )

        self.avro_key_deserializer = AvroDeserializer(
            schema_registry_client=self.schema_registry_client,
            schema_str=self.key_schema,
        )

        self.avro_value_serializer = AvroSerializer(
            conf={"auto.register.schemas": False},
            schema_registry_client=self.schema_registry_client,
            schema_str=self.value_schema,
        )

        self.avro_value_deserializer = AvroDeserializer(
            schema_registry_client=self.schema_registry_client,
            schema_str=self.value_schema,
        )

        self.key_context = SerializationContext(
            self.topic_name,
            MessageField.KEY,
        )

        self.value_context = SerializationContext(
            self.topic_name,
            MessageField.VALUE,
        )

    def serialize_key(self, obj: object) -> bytes:
        return self.avro_key_serializer(  # type: ignore
            obj=obj,
            ctx=self.key_context,
        )

    def serialize_value(self, obj: object) -> bytes:
        return self.avro_value_serializer(  # type: ignore
            obj=obj,
            ctx=self.value_context,
        )

    def deserialize_key(self, data: bytes) -> object:
        return self.avro_key_deserializer(  # type: ignore
            data=data,
            ctx=self.key_context,
        )

    def deserialize_value(self, data: bytes) -> object:
        return self.avro_value_deserializer(  # type: ignore
            data=data,
            ctx=self.value_context,
        )


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

"""Serializes and deserializes using AVRO and schema registry."""

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


class AvroParser:
    """Parser that serializes and deserializes Python objects."""

    def __init__(
        self,
        schema_registry_client: SchemaRegistryClient,
        schema_subject: str,
        schema_version: int,
        topic_name: str,
    ) -> None:
        """Initialize an AvroParser.

        Args:
            schema_registry_client (SchemaRegistryClient): Client to communicate with the schema registry.
            schema_subject (str): Schema subject to use.
            schema_version (int): Schema version to use.
            topic_name (str): Kafka topic the schema is associated with (messages published and consumed from).
        """
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
        """Python object to bytes."""
        return self.avro_key_serializer(  # type: ignore
            obj=obj,
            ctx=self.key_context,
        )

    def serialize_value(self, obj: object) -> bytes:
        """Python object to bytes."""
        return self.avro_value_serializer(  # type: ignore
            obj=obj,
            ctx=self.value_context,
        )

    def deserialize_key(self, data: bytes) -> object:
        """Bytes to Python object."""
        return self.avro_key_deserializer(  # type: ignore
            data=data,
            ctx=self.key_context,
        )

    def deserialize_value(self, data: bytes) -> object:
        """Bytes to Python object."""
        return self.avro_value_deserializer(  # type: ignore
            data=data,
            ctx=self.value_context,
        )

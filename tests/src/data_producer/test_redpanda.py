import json
import os

import requests
from helpers.container.redpanda import RedpandaContainer
from kafka import KafkaAdminClient, KafkaConsumer, KafkaProducer, TopicPartition
from kafka.admin import NewTopic

# Because of windows, this needs to be specified.
os.environ["TC_HOST"] = "localhost"


def produce_and_consume_message(container: RedpandaContainer):
    topic = "test-topic"
    bootstrap_server = container.get_bootstrap_server()

    admin = KafkaAdminClient(bootstrap_servers=[bootstrap_server])
    admin.create_topics([NewTopic(topic, 1, 1)])

    producer = KafkaProducer(bootstrap_servers=[bootstrap_server])
    future = producer.send(topic, b"verification message")
    future.get(timeout=10)
    producer.close()

    consumer = KafkaConsumer(bootstrap_servers=[bootstrap_server])
    tp = TopicPartition(topic, 0)
    consumer.assign([tp])
    consumer.seek_to_beginning()
    assert (
        consumer.end_offsets([tp])[tp] == 1
    ), "Expected exactly one test message to be present on test topic !"


def test_redpanda_producer_consumer(fixture_redpanda_container: RedpandaContainer):
    produce_and_consume_message(fixture_redpanda_container)


def test_schema_registry(fixture_redpanda_container: RedpandaContainer):
    address = fixture_redpanda_container.get_schema_registry_address()
    subject_name = "test-subject-value"
    url = f"{address}/subjects"

    payload = {"schema": json.dumps({"type": "string"})}
    headers = {"Content-Type": "application/vnd.schemaregistry.v1+json"}
    create_result = requests.post(
        f"{url}/{subject_name}/versions",
        data=json.dumps(payload),
        headers=headers,
        timeout=1,
    )
    assert create_result.status_code == 200

    result = requests.get(url, timeout=1)
    assert result.status_code == 200
    assert subject_name in result.json()

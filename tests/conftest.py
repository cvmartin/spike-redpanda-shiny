import asyncio
import os
from typing import Any, AsyncGenerator, Generator

import orjson
import pytest
import pytest_asyncio
from aiokafka import AIOKafkaProducer

from tests.helpers.container.redpanda import RedpandaContainer


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, Any, Any]:
    """Overrides pytest default function scoped event loop.

    This fixture should not be renamed, see
    https://github.com/tortoise/tortoise-orm/issues/638
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def fixture_redpanda_container() -> Generator[RedpandaContainer, Any, Any]:
    """Provides a redpanda container ready to use."""
    # Necessary to specify this to in Windows the container host
    # is recognized as `localhost`.
    os.environ["TC_HOST"] = "localhost"

    container = RedpandaContainer()
    container.start()
    yield container
    container.stop()


@pytest_asyncio.fixture(scope="session")
async def fixture_async_kafka_producer(
    fixture_redpanda_container: RedpandaContainer,
) -> AsyncGenerator[AIOKafkaProducer, Any]:
    """Provides an asynchronous kafka producer ready to use."""
    producer = AIOKafkaProducer(
        bootstrap_servers=fixture_redpanda_container.get_bootstrap_server(),
        value_serializer=lambda x: orjson.dumps(x),
    )
    await producer.start()
    yield producer
    await producer.stop()

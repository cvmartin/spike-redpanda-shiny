# Base image with Python and Kafka installed
FROM python:3.11


COPY ./ ./

RUN pip install --no-cache-dir --upgrade "."

CMD ["python", "./docker_deploy/kafka_producer/entrypoint.py"]

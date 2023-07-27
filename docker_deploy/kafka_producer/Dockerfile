# Base image with Python and Kafka installed
FROM python:3.11

# Install required packages
RUN pip install kafka-python

# Copy the Python script into the container
COPY docker_deploy/kafka_producer/data_producer.py /data_producer.py

# Command to run the Python script
CMD ["python", "/data_producer.py"]

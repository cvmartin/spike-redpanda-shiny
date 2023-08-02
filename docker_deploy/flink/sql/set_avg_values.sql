SET 'pipeline.name' = 'Set average values';

CREATE TABLE meter_values(
    meter_id VARCHAR,
    measurement DOUBLE,
    event_timestamp DOUBLE,
    event_datetime_ltz AS TO_TIMESTAMP_LTZ(CAST(event_timestamp * 1000 AS BIGINT), 3),
    WATERMARK FOR event_datetime_ltz AS event_datetime_ltz - INTERVAL '10' SECOND,
    proc_datetime AS PROCTIME()
) WITH (
    'connector' = 'kafka',
    'topic' = 'meter_measurements',
    'properties.bootstrap.servers' = 'redpanda-1:29092',
    'properties.group.id' = 'test-group',
    'properties.auto.offset.reset' = 'earliest',
    'format' = 'json'
);

CREATE TABLE avg_meter_values(
    meter_id VARCHAR,
    avg_measurement DOUBLE,
    timestamp_window_start BIGINT,
    timestamp_window_end BIGINT
) WITH (
    'connector' = 'kafka',
    'topic' = 'avg_meter_values',
    'properties.bootstrap.servers' = 'redpanda-1:29092',
    'properties.group.id' = 'test-group',
    'properties.auto.offset.reset' = 'earliest',
    'format' = 'json'
);

CREATE TABLE sum_meter_values(
    sum_measurement DOUBLE,
    timestamp_window_start BIGINT,
    timestamp_window_end BIGINT
) WITH (
    'connector' = 'kafka',
    'topic' = 'sum_meter_values',
    'properties.bootstrap.servers' = 'redpanda-1:29092',
    'properties.group.id' = 'test-group',
    'properties.auto.offset.reset' = 'earliest',
    'format' = 'json'
);

INSERT INTO avg_meter_values
SELECT
    meter_id,
    AVG(measurement) AS avg_measurement,
    UNIX_TIMESTAMP(CAST(TUMBLE_START(event_datetime_ltz, INTERVAL '10' SECONDS) AS STRING)) AS timestamp_window_start,
    UNIX_TIMESTAMP(CAST(TUMBLE_END(event_datetime_ltz, INTERVAL '10' SECONDS) AS STRING)) AS timestamp_window_end
FROM meter_values
GROUP BY
    TUMBLE(event_datetime_ltz, INTERVAL '10' SECONDS),
    meter_id;

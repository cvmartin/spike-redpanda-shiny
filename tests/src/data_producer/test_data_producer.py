import datetime

from data_producer.data_producer import MessageMeterMeasurement


class TestMessageMeterMeasurement:
    def test_to_from_json(self):
        message_initial = MessageMeterMeasurement(
            meter_id="test_id",
            measurement=42,
            event_timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
        )

        message_reconstructed = MessageMeterMeasurement.from_json(
            json_string=message_initial.to_json(),
        )

        assert message_initial == message_reconstructed

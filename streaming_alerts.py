import os
import json
import logging
from dotenv import load_dotenv
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

log = logging.getLogger(__name__)

# Load Environment Variables
load_dotenv()
KAFKA_BROKER = os.getenv("KAFKA_BROKER")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC_SENSOR_DATA")

# Alerting Thresholds
TEMP_THRESHOLD = 45.0
HUMIDITY_THRESHOLD = 85.0


def main():
    """
    Main function to connect to Kafka and run the alerting loop.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    consumer = None
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            # Automatically deserialize JSON messages
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            # Start reading the latest messages, ignore old ones
            auto_offset_reset="latest",
            # A unique ID for this consumer group
            group_id="real-time-alerts-group",
        )
        log.info(f"Connected to Kafka: {KAFKA_BROKER}, Topic: {KAFKA_TOPIC}")
    except NoBrokersAvailable:
        log.error(f"Error: Could not connect to Kafka broker at {KAFKA_BROKER}")
        log.error("Please ensure Kafka is running and accessible.")
        exit(1)
    except Exception as e:
        log.error(f"An error occurred connecting to Kafka: {e}")
        exit(1)

    log.info("Listening for real-time messages... Press Ctrl+C to stop.")

    try:
        # This is the infinite loop. It will block and wait for new messages.
        for message in consumer:
            data = message.value

            # log.info(f"Received: {data}")

            # Alert Logic
            try:
                if data["temperature"] > TEMP_THRESHOLD:
                    log.warning(
                        f"[!!! ALERT !!!] High Temperature: {data['temperature']}°C (Sensor: {data['sensor_id']})"
                    )

                elif data["humidity"] > HUMIDITY_THRESHOLD:
                    log.warning(
                        f"[!!! ALERT !!!] High Humidity: {data['humidity']}% (Sensor: {data['sensor_id']})"
                    )

            except:
                log.error(f"Received malformed data: {data}")

    except KeyboardInterrupt:
        log.info("Stopping consumer.")
    finally:
        if consumer:
            consumer.close()
            log.info("Kafka consumer closed.")


if __name__ == "__main__":
    main()

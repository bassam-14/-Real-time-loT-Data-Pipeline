import random
from datetime import datetime
import time
import json
import os
import logging
from dotenv import load_dotenv
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

log = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
KAFKA_BROKER = os.getenv("KAFKA_BROKER")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC_SENSOR_DATA")

TOTAL_SENSORS = 50
ANOMALY_CHANCE = 0.05  # A 5% chance of an anomalous reading
REJECTED_DATA = 0.01


def generate_sensor_reading():
    """
    Simulates a single data reading from a random IoT sensor, with a
    chance of producing an anomalous value for temperature and humidity.
    """
    sensor_id = random.randint(1, TOTAL_SENSORS)
    timestamp = datetime.now().isoformat()

    randomness = random.random()
    # Simulate temperature reading.
    if randomness > ANOMALY_CHANCE:
        temperature = round(random.uniform(15.0, 30.0), 2)
    elif randomness < REJECTED_DATA:
        sensor_id *= -1
        temperature = round(random.uniform(45.0, 60.0), 2)
    elif randomness < ANOMALY_CHANCE:
        temperature = round(random.uniform(45.0, 60.0), 2)

    # Simulate humidity reading, independent of the temperature.
    if random.random() > ANOMALY_CHANCE:
        humidity = round(random.uniform(40.0, 60.0), 2)
    else:
        humidity = round(random.uniform(85.0, 100.0), 2)

    # Assemble the final data point into a dictionary for easy use.
    reading = {
        "sensor_id": sensor_id,
        "timestamp": timestamp,
        "temperature": temperature,
        "humidity": humidity,
    }
    return reading


def main():
    """
    Main function to run the data simulation loop.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    producer = None
    try:
        # Set up the Kafka producer
        # This will automatically serialize the dictionary into JSON bytes
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        log.info(f"Connected to Kafka broker at {KAFKA_BROKER}")
    except NoBrokersAvailable:
        log.error(f"Error: Could not connect to Kafka broker at {KAFKA_BROKER}")
        log.error("Please ensure Kafka is running and accessible.")
        exit(1)
    except Exception as e:
        log.error(f"An error occurred connecting to Kafka: {e}")
        exit(1)

    log.info("Starting IoT Data Simulator...")
    log.info(f"Sending data to topic: {KAFKA_TOPIC}")
    log.info("Press Ctrl+C to stop.")

    try:
        # This is the main loop that runs indefinitely.
        while True:
            data_point = generate_sensor_reading()

            # Send the data point to the Kafka topic
            producer.send(KAFKA_TOPIC, value=data_point)
            print(f"Sent data: {data_point}")

            producer.flush()  # Ensure the message is sent

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nSimulator stopped.")


if __name__ == "__main__":
    main()

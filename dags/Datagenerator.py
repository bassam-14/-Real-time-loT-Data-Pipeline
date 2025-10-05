import random
from datetime import datetime
import time
import json

TOTAL_SENSORS = 50
ANOMALY_CHANCE = 0.05  # A 5% chance of an anomalous reading


def generate_sensor_reading():
    """
    Simulates a single data reading from a random IoT sensor, with a
    chance of producing an anomalous value for temperature and humidity.
    """
    sensor_id = random.randint(1, TOTAL_SENSORS)
    timestamp = datetime.now().isoformat()

    # Simulate temperature reading.
    if random.random() > ANOMALY_CHANCE:
        temperature = round(random.uniform(15.0, 30.0), 2)
    else:
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
    print("Starting IoT Data Simulator...")
    print("Press Ctrl+C to stop.")

    try:
        # This is the main loop that runs indefinitely.
        while True:
            data_point = generate_sensor_reading()

            # Dump the data point as a JSON string to Kafka (Later).
            print(json.dumps(data_point))
            with open("logs/sample_logs.txt", "a") as file:
                file.write(f"\n{json.dumps(data_point)}")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nSimulator stopped.")


if __name__ == "__main__":
    main()

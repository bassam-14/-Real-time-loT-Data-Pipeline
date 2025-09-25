import random
from datetime import datetime

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

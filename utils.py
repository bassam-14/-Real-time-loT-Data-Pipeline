"""
Utility script for common IoT Data Pipeline operations
Run this script to perform various maintenance and testing tasks
"""

import json
import sys
from datetime import datetime


def print_banner(text):
    """Print a formatted banner"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def test_kafka_connection():
    """Test Kafka connection"""
    print_banner("Testing Kafka Connection")
    try:
        from kafka import KafkaProducer, KafkaConsumer
        from kafka.admin import KafkaAdminClient, NewTopic

        # Test producer
        print("📡 Testing Kafka Producer...")
        producer = KafkaProducer(
            bootstrap_servers=["localhost:9092"],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        # Send test message
        test_data = {
            "sensor_id": 999,
            "timestamp": datetime.now().isoformat(),
            "temperature": 25.5,
            "humidity": 50.0,
            "test": True,
        }

        producer.send("test-topic", test_data)
        producer.flush()
        producer.close()
        print("✅ Kafka Producer: OK")

        # Test consumer
        print("\n📡 Testing Kafka Consumer...")
        consumer = KafkaConsumer(
            "test-topic",
            bootstrap_servers=["localhost:9092"],
            auto_offset_reset="earliest",
            consumer_timeout_ms=5000,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )

        messages = []
        for message in consumer:
            messages.append(message.value)
            if len(messages) >= 1:
                break

        consumer.close()

        if messages:
            print("✅ Kafka Consumer: OK")
            print(f"📨 Received message: {messages[0]}")
        else:
            print("⚠️  No messages received (this is normal if topic is empty)")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 Make sure:")
        print("  1. Docker services are running: docker-compose ps")
        print("  2. Kafka is healthy: docker-compose logs kafka")
        return False


def test_mysql_connection():
    """Test MySQL connection"""
    print_banner("Testing MySQL Connection")
    try:
        import pymysql

        print("🗄️  Connecting to MySQL...")
        connection = pymysql.connect(
            host="localhost",
            port=3306,
            user="airflow",
            password="airflow",
            database="airflow_db",
        )

        cursor = connection.cursor()

        # Get MySQL version
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"✅ MySQL Connection: OK (Version {version})")

        # Get database info
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]
        print(f"📊 Current Database: {db_name}")

        # Get table count
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"📋 Number of Tables: {len(tables)}")

        cursor.close()
        connection.close()

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 Make sure:")
        print("  1. Docker services are running: docker-compose ps")
        print("  2. MySQL is healthy: docker-compose logs mysql")
        print("  3. Credentials in .env are correct")
        return False


def create_sensor_table():
    """Create sensor_readings table in MySQL"""
    print_banner("Creating Sensor Readings Table")
    try:
        import pymysql

        connection = pymysql.connect(
            host="localhost",
            port=3306,
            user="airflow",
            password="airflow",
            database="airflow_db",
        )

        cursor = connection.cursor()

        # Create table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sensor_id INT NOT NULL,
            timestamp DATETIME NOT NULL,
            temperature FLOAT NOT NULL,
            humidity FLOAT NOT NULL,
            is_anomaly BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_sensor_timestamp (sensor_id, timestamp),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """

        cursor.execute(create_table_sql)
        connection.commit()

        print("✅ Table 'sensor_readings' created successfully!")

        # Show table structure
        cursor.execute("DESCRIBE sensor_readings")
        columns = cursor.fetchall()

        print("\n📋 Table Structure:")
        print(f"{'Field':<20} {'Type':<20} {'Null':<10} {'Key':<10}")
        print("-" * 60)
        for col in columns:
            print(f"{col[0]:<20} {col[1]:<20} {col[2]:<10} {col[3]:<10}")

        cursor.close()
        connection.close()

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def generate_sample_data(num_records=10):
    """Generate and send sample sensor data to Kafka"""
    print_banner(f"Generating {num_records} Sample Sensor Records")
    try:
        import random
        from kafka import KafkaProducer

        producer = KafkaProducer(
            bootstrap_servers=["localhost:9092"],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        topic = "iot_sensor_data"

        for i in range(num_records):
            # Generate random sensor data
            sensor_id = random.randint(1, 50)

            # Normal vs anomaly
            is_anomaly = random.random() < 0.05

            if is_anomaly:
                temperature = round(random.uniform(45.0, 60.0), 2)
                humidity = round(random.uniform(85.0, 100.0), 2)
            else:
                temperature = round(random.uniform(15.0, 30.0), 2)
                humidity = round(random.uniform(40.0, 60.0), 2)

            data = {
                "sensor_id": sensor_id,
                "timestamp": datetime.now().isoformat(),
                "temperature": temperature,
                "humidity": humidity,
                "is_anomaly": is_anomaly,
            }

            producer.send(topic, data)
            print(
                f"  📤 Sent: Sensor {sensor_id} | Temp: {temperature}°C | Humidity: {humidity}% | Anomaly: {is_anomaly}"
            )

        producer.flush()
        producer.close()

        print(f"\n✅ Successfully sent {num_records} records to topic '{topic}'")
        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 Make sure the topic exists:")
        print(
            "  docker-compose exec kafka kafka-topics --create --bootstrap-server localhost:29092 --topic iot_sensor_data --partitions 3"
        )
        return False


def check_system_status():
    """Check the status of all services"""
    print_banner("System Status Check")
    import subprocess

    try:
        # Check Docker services
        print("🐳 Docker Services Status:")
        result = subprocess.run(
            ["docker-compose", "ps"], capture_output=True, text=True, shell=True
        )
        print(result.stdout)

        # Check Kafka topics
        print("\n📊 Kafka Topics:")
        result = subprocess.run(
            [
                "docker-compose",
                "exec",
                "kafka",
                "kafka-topics",
                "--list",
                "--bootstrap-server",
                "localhost:29092",
            ],
            capture_output=True,
            text=True,
            shell=True,
        )

        if result.returncode == 0:
            topics = result.stdout.strip().split("\n")
            for topic in topics:
                if topic:
                    print(f"  • {topic}")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main_menu():
    """Display main menu and handle user input"""
    while True:
        print_banner("IoT Data Pipeline Utilities")
        print("1. Test Kafka Connection")
        print("2. Test MySQL Connection")
        print("3. Create Sensor Readings Table")
        print("4. Generate Sample Data (10 records)")
        print("5. Generate Sample Data (100 records)")
        print("6. Check System Status")
        print("7. Run All Tests")
        print("0. Exit")
        print()

        choice = input("Enter your choice (0-7): ").strip()

        if choice == "1":
            test_kafka_connection()
        elif choice == "2":
            test_mysql_connection()
        elif choice == "3":
            create_sensor_table()
        elif choice == "4":
            generate_sample_data(10)
        elif choice == "5":
            generate_sample_data(100)
        elif choice == "6":
            check_system_status()
        elif choice == "7":
            print_banner("Running All Tests")
            test_kafka_connection()
            test_mysql_connection()
            create_sensor_table()
        elif choice == "0":
            print("\n👋 Goodbye!\n")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please try again.")

        input("\n⏎ Press Enter to continue...")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

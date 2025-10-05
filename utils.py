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

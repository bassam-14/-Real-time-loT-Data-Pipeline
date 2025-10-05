#!/bin/bash
# Bash Setup Script for IoT Data Pipeline (Linux/Mac)
# Run this script to set up the environment on Linux/Mac

echo "🚀 Setting up IoT Data Pipeline Environment..."

# Check if Docker is running
echo ""
echo "📋 Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi
echo "✅ Docker is running"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "📋 Creating .env file from sample..."
    cp sample.env .env
    echo "✅ .env file created. Please edit it with your credentials!"
    echo "⚠️  Remember to change default passwords!"
else
    echo ""
    echo "✅ .env file already exists"
fi

# Create required directories
echo ""
echo "📋 Creating required directories..."
for dir in dags logs plugins config; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "  ✅ Created $dir/"
    else
        echo "  ✅ $dir/ already exists"
    fi
done

# Set AIRFLOW_UID
echo ""
echo "📋 Setting AIRFLOW_UID..."
echo "AIRFLOW_UID=$(id -u)" >> .env
echo "✅ AIRFLOW_UID set to $(id -u)"

# Fix permissions
echo ""
echo "📋 Setting correct permissions..."
sudo chown -R $(id -u):$(id -g) dags logs plugins config
echo "✅ Permissions set"

# Initialize Airflow
echo ""
echo "📋 Initializing Airflow (this may take a few minutes)..."
docker-compose up airflow-init
if [ $? -eq 0 ]; then
    echo "✅ Airflow initialized successfully"
else
    echo "❌ Error initializing Airflow"
    exit 1
fi

# Start all services
echo ""
echo "📋 Starting all services..."
docker-compose up -d
if [ $? -eq 0 ]; then
    echo "✅ All services started successfully"
else
    echo "❌ Error starting services"
    exit 1
fi

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be healthy (30 seconds)..."
sleep 30

# Check service status
echo ""
echo "📋 Service Status:"
docker-compose ps

# Print access information
echo ""
echo "✅ Setup Complete!"
echo ""
echo "🌐 Access URLs:"
echo "  • Airflow UI:  http://localhost:8080"
echo "    Username: airflow | Password: airflow (or your custom credentials)"
echo "  • Kafka UI:    http://localhost:8090"
echo "  • MySQL:       localhost:3306"
echo ""
echo "📚 Next Steps:"
echo "  1. Open Airflow UI at http://localhost:8080"
echo "  2. Create Kafka topics: docker-compose exec kafka kafka-topics --create --bootstrap-server localhost:29092 --topic iot_sensor_data --partitions 3"
echo "  3. Add your DAG files to the dags/ folder"
echo ""
echo "💡 Tips:"
echo "  • View logs: docker-compose logs -f"
echo "  • Stop services: docker-compose stop"
echo "  • Remove everything: docker-compose down -v"
echo ""
echo "Happy Data Engineering! 🚀"

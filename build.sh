#!/bin/bash
# Build Script for IoT Data Pipeline (Linux/Mac)
# This script builds the custom Airflow Docker image with all dependencies

echo "🔨 Building IoT Data Pipeline Docker Image..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Build the custom Airflow image
echo "📦 Building custom Airflow image (this may take 5-10 minutes)..."
echo "   This installs all Python packages from requirements.txt"
echo ""

docker-compose build --no-cache

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Docker image built successfully!"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Run: ./setup.sh  (to initialize and start services)"
    echo "   OR"
    echo "   2. Run: docker-compose up -d  (if already initialized)"
    echo ""
else
    echo ""
    echo "❌ Build failed! Check the error messages above."
    echo ""
    echo "💡 Common issues:"
    echo "   • Check requirements.txt syntax"
    echo "   • Ensure Dockerfile exists"
    echo "   • Check Docker has enough disk space"
    exit 1
fi

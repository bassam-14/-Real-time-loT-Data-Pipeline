# How Requirements.txt Works in This Project

## 📦 Overview

This project uses Docker to run Apache Airflow and related services. The Python dependencies listed in `requirements.txt` are installed into a **custom Docker image** that extends the official Apache Airflow image.

## 🔧 How It Works

### 1. Dockerfile

The `Dockerfile` in the project root:

```dockerfile
FROM apache/airflow:3.1.0
USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
```

This file:

- Starts from the official Airflow 3.1.0 image
- Copies your `requirements.txt` into the image
- Installs all packages listed in requirements.txt

### 2. Docker Compose Build

The `docker-compose.yaml` is configured to build this custom image:

```yaml
x-airflow-common: &airflow-common
  build:
    context: .
    dockerfile: Dockerfile
  image: iot-airflow:latest
```

### 3. All Services Use the Custom Image

All Airflow services (webserver, scheduler, worker, etc.) use this custom-built image, so they all have access to the packages from requirements.txt.

## 🚀 Building the Image

### Automatic Build (Recommended)

Run the setup script which automatically builds the image:

```powershell
# Windows
.\setup.ps1

# Linux/Mac
./setup.sh
```

### Manual Build

If you need to rebuild after updating requirements.txt:

```powershell
# Build the image
docker-compose build

# Or use the dedicated build script
.\build.ps1  # Windows
./build.sh   # Linux/Mac
```

### Rebuild After Changes

When you modify `requirements.txt`, rebuild the image:

```powershell
# Stop services
docker-compose down

# Rebuild with no cache (ensures fresh install)
docker-compose build --no-cache

# Start services with new image
docker-compose up -d
```

## 📝 Adding New Packages

### Step 1: Edit requirements.txt

Add your package to `requirements.txt`:

```txt
pandas
kafka-python
your-new-package>=1.0.0
```

### Step 2: Rebuild

```powershell
docker-compose build
```

### Step 3: Restart Services

```powershell
docker-compose up -d
```

The new package is now available in all Airflow containers!

## 🔍 Verifying Installed Packages

Check what packages are installed:

```powershell
# List all installed packages
docker-compose exec airflow-apiserver pip list

# Check specific package
docker-compose exec airflow-apiserver pip show kafka-python

# Test import in Python
docker-compose exec airflow-apiserver python -c "import kafka; print(kafka.__version__)"
```

## 🎯 Why This Approach?

### ✅ Advantages:

1. **Consistent Environment**: All team members have identical packages
2. **Version Control**: requirements.txt is tracked in Git
3. **Fast Startup**: Packages pre-installed in image, not at runtime
4. **Reproducible**: Rebuild anytime to get same environment
5. **Portable**: Image can be shared or deployed anywhere

### ❌ Alternative Approach (Not Used):

Some setups use `_PIP_ADDITIONAL_REQUIREMENTS` environment variable:

```yaml
_PIP_ADDITIONAL_REQUIREMENTS: "kafka-python pymysql"
```

**Why we don't use this:**

- Installs packages on every container start (slower)
- Harder to version control
- Less reliable for production
- More difficult to debug

## 🐳 Docker Image Layers

The custom image has these layers:

```
[Base: apache/airflow:3.1.0]
    ↓
[System packages and Airflow core]
    ↓
[Your requirements.txt packages] ← Custom layer
    ↓
[Final image: iot-airflow:latest]
```

## 🔄 Workflow Summary

```
1. Edit requirements.txt
   ↓
2. Run: docker-compose build
   ↓
3. Docker builds custom image with packages
   ↓
4. Run: docker-compose up -d
   ↓
5. All services use the new image with packages
```

## 🎓 Understanding the Build Process

When you run `docker-compose build`:

1. **Docker reads Dockerfile**

   - Pulls base image: `apache/airflow:3.1.0`

2. **Copies requirements.txt into image**

   - `COPY requirements.txt /requirements.txt`

3. **Installs packages**

   - `RUN pip install -r /requirements.txt`
   - Downloads and installs each package
   - Creates Python environment with all dependencies

4. **Tags final image**

   - Saves as: `iot-airflow:latest`

5. **Docker Compose uses this image**
   - All Airflow services reference this image
   - No need to reinstall on each start

## 📊 Requirements.txt in This Project

Current packages installed:

- **pandas**: Data manipulation
- **apache-airflow-providers-mysql**: MySQL integration
- **mysql-connector-python**: MySQL driver
- **pymysql**: Pure Python MySQL client
- **kafka-python**: Kafka Python client
- **confluent-kafka**: Confluent's Kafka client
- **sqlalchemy**: SQL toolkit
- **numpy**: Numerical computing
- **pytz**: Timezone support
- **python-json-logger**: JSON logging

## 🆘 Troubleshooting

### Build Fails

```powershell
# Clear Docker build cache
docker builder prune

# Rebuild without cache
docker-compose build --no-cache
```

### Package Not Found

```powershell
# Verify requirements.txt syntax
cat requirements.txt

# Check package exists on PyPI
pip search <package-name>
```

### Old Packages Still Present

```powershell
# Remove old containers
docker-compose down

# Rebuild image
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

### Want to Test Locally (Without Docker)

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Install packages
pip install -r requirements.txt

# Test
python utils.py
```

## 💡 Pro Tips

1. **Pin Versions**: Use exact versions for production

   ```txt
   kafka-python==2.0.2
   pandas==2.1.0
   ```

2. **Comments**: Document why packages are needed

   ```txt
   # Kafka streaming
   kafka-python>=2.0.2
   confluent-kafka>=2.3.0
   ```

3. **Separate Dev Dependencies**: Create requirements-dev.txt for testing tools

4. **Regular Updates**: Keep packages updated for security
   ```powershell
   pip list --outdated
   ```

---

**Summary**: `requirements.txt` → `Dockerfile` → `docker-compose build` → Custom Docker Image → All Airflow Services Use It! 🎉

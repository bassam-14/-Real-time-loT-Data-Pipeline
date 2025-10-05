# Project Architecture & Setup Flow

## 📁 File Structure & Purpose

```
final project/
│
├── 🐳 Docker Configuration
│   ├── Dockerfile              ← Builds custom Airflow image with requirements.txt
│   ├── docker-compose.yaml     ← Defines all services (Airflow, Kafka, MySQL, etc.)
│   ├── .dockerignore          ← Excludes files from Docker build
│   └── requirements.txt        ← Python packages to install in Docker image
│
├── ⚙️ Configuration Files
│   ├── .env                    ← Your secrets (create from sample.env)
│   ├── sample.env             ← Template for environment variables
│   └── config/
│       └── airflow.cfg        ← Airflow configuration
│
├── 📝 Application Code
│   ├── dags/                  ← Your Airflow DAG files go here
│   │   └── Datagenerator.py   ← Sample sensor data generator
│   ├── plugins/               ← Custom Airflow plugins
│   └── logs/                  ← Application logs (auto-generated)
│
├── 🛠️ Setup & Build Scripts
│   ├── setup.ps1              ← Windows: Full setup (builds + initializes + starts)
│   ├── setup.sh               ← Linux/Mac: Full setup
│   ├── build.ps1              ← Windows: Just build Docker image
│   ├── build.sh               ← Linux/Mac: Just build Docker image
│   └── commands.ps1           ← PowerShell helper functions
│
├── 🧪 Utilities
│   └── utils.py               ← Testing and helper script
│
└── 📚 Documentation
    ├── README.md              ← Main project documentation
    ├── TEAM_SETUP.md          ← Team member onboarding guide
    ├── QUICK_REFERENCE.md     ← Command cheat sheet
    ├── REQUIREMENTS_EXPLAINED.md ← How requirements.txt works
    ├── SETUP_SUMMARY.md       ← What was configured
    └── ARCHITECTURE.md        ← This file
```

## 🔄 How Everything Connects

### 1️⃣ Build Phase (Requirements.txt → Docker Image)

```
┌─────────────────────┐
│  requirements.txt   │  List of Python packages
│  - kafka-python     │  (pandas, pymysql, kafka, etc.)
│  - pymysql          │
│  - confluent-kafka  │
└──────────┬──────────┘
           │ Used by
           ▼
┌─────────────────────┐
│    Dockerfile       │  Instructions to build custom image
│  FROM airflow:3.1   │  1. Start from official Airflow
│  COPY requirements  │  2. Copy requirements.txt
│  RUN pip install   │  3. Install all packages
└──────────┬──────────┘
           │ Executed by
           ▼
┌─────────────────────┐
│  docker-compose     │  Build command creates image
│      build          │  docker-compose build
└──────────┬──────────┘
           │ Creates
           ▼
┌─────────────────────┐
│ iot-airflow:latest  │  Custom Docker image with
│  - Airflow 3.1      │  all your packages installed
│  - All packages     │  Ready to use!
└─────────────────────┘
```

### 2️⃣ Runtime Phase (Docker Image → Services)

```
┌─────────────────────────────────────────────────────┐
│         docker-compose.yaml                         │
│  Defines all services and uses the custom image     │
└─────────────┬───────────────────────────────────────┘
              │ docker-compose up -d
              ▼
    ┌─────────────────────┐
    │  iot-airflow:latest │  Custom image
    │  (with packages)    │
    └─────────┬───────────┘
              │ Used by all Airflow services
              ├──────┬──────┬──────┬──────┐
              ▼      ▼      ▼      ▼      ▼
    ┌─────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐
    │API  │ │Sched│ │Work│ │Trig│ │DAG │
    │Serv │ │uler │ │er  │ │ger │ │Proc│
    └─────┘ └────┘ └────┘ └────┘ └────┘
    All have access to kafka-python, pymysql, etc.
```

### 3️⃣ Complete System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  IoT Data Pipeline System                │
└─────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Host Machine (Windows/Linux/Mac)                        │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Docker Desktop                                  │    │
│  │                                                  │    │
│  │  ┌────────────────────────────────────────┐    │    │
│  │  │ Network: default                       │    │    │
│  │  │                                        │    │    │
│  │  │  ┌──────────────┐  ┌──────────────┐  │    │    │
│  │  │  │   Zookeeper  │  │    Kafka     │  │    │    │
│  │  │  │   :2181      │◄─┤   :9092      │  │    │    │
│  │  │  └──────────────┘  └──────┬───────┘  │    │    │
│  │  │                            │          │    │    │
│  │  │  ┌──────────────┐  ┌──────▼───────┐  │    │    │
│  │  │  │   Kafka UI   │  │  Airflow     │  │    │    │
│  │  │  │   :8090      │  │  Services    │  │    │    │
│  │  │  └──────────────┘  │  :8080       │  │    │    │
│  │  │                    │              │  │    │    │
│  │  │  ┌──────────────┐  │ • API Server│  │    │    │
│  │  │  │    MySQL     │◄─┤ • Scheduler │  │    │    │
│  │  │  │    :3306     │  │ • Worker    │  │    │    │
│  │  │  └──────────────┘  │ • Triggerer │  │    │    │
│  │  │                    │ • DAG Proc  │  │    │    │
│  │  │  ┌──────────────┐  └──────▲───────┘  │    │    │
│  │  │  │    Redis     │         │          │    │    │
│  │  │  │    :6379     │◄────────┘          │    │    │
│  │  │  └──────────────┘                    │    │    │
│  │  └────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
│  Volumes (persistent data):                              │
│  • mysql-db-volume  → MySQL data                         │
│  • ./dags          → DAG files                           │
│  • ./logs          → Application logs                    │
│  • ./plugins       → Custom plugins                      │
│  • ./config        → Configuration                       │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Access Points                                            │
│  • http://localhost:8080  → Airflow UI                   │
│  • http://localhost:8090  → Kafka UI                     │
│  • localhost:9092         → Kafka (from host)            │
│  • localhost:3306         → MySQL (from host)            │
└──────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

### Streaming Path (Real-time)

```
Sensor Data Generator (DAG)
         ↓
    [Produce to Kafka Topic: iot_sensor_data]
         ↓
    Kafka Broker (Port 9092)
         ↓
    [Kafka Consumer (in Airflow DAG)]
         ↓
    Process & Transform
         ↓
    Store in MySQL
```

### Batch Processing Path

```
Airflow Scheduler (checks DAGs every 30s)
         ↓
    Trigger DAG Run
         ↓
    Airflow Worker executes tasks
         ↓
    Task 1: Read from MySQL
    Task 2: Process data
    Task 3: Generate reports
    Task 4: Store results
```

## 🚀 Setup Flow

### Initial Setup (One Time)

```
1. Clone repository
   ↓
2. Copy sample.env → .env (edit credentials)
   ↓
3. Run setup.ps1 or setup.sh
   ├─ Check Docker running
   ├─ Create directories
   ├─ Build Docker image (uses requirements.txt)
   ├─ Initialize Airflow database
   └─ Start all services
   ↓
4. Create Kafka topics
   ↓
5. Access UIs and start developing
```

### Daily Development Workflow

```
1. git pull (get latest code)
   ↓
2. docker-compose up -d (start if stopped)
   ↓
3. Add/Edit DAGs in dags/ folder
   ↓
4. Airflow auto-detects new DAGs (30-60s)
   ↓
5. Test in Airflow UI
   ↓
6. git commit & push changes
```

### Adding New Python Packages

```
1. Edit requirements.txt
   (add: new-package>=1.0.0)
   ↓
2. docker-compose down
   ↓
3. docker-compose build --no-cache
   ↓
4. docker-compose up -d
   ↓
5. Verify: docker-compose exec airflow-apiserver pip list
```

## 🎯 Key Concepts

### Why Docker?

- ✅ Consistent environment across all team members
- ✅ Easy to start/stop entire stack
- ✅ Isolated from your host system
- ✅ Easy to scale and deploy

### Why Custom Dockerfile?

- ✅ Pre-install all Python packages
- ✅ Fast container startup
- ✅ Version-controlled dependencies
- ✅ Reproducible builds

### Why Docker Compose?

- ✅ Define multiple services in one file
- ✅ Manage service dependencies
- ✅ Easy networking between containers
- ✅ Single command to manage everything

## 📊 Service Dependencies

```
┌──────────────┐
│  Zookeeper   │  (No dependencies)
└──────┬───────┘
       │ requires
       ▼
┌──────────────┐
│    Kafka     │  (Needs Zookeeper)
└──────┬───────┘
       │
┌──────────────┐
│    MySQL     │  (No dependencies)
└──────┬───────┘
       │
┌──────────────┐
│    Redis     │  (No dependencies)
└──────┬───────┘
       │
       │ All three required by
       ▼
┌──────────────┐
│   Airflow    │  (Needs MySQL, Redis, Kafka)
│   Services   │
└──────────────┘
```

Docker Compose ensures services start in correct order using `depends_on` and health checks!

## 💡 Understanding the Magic

**Question**: How does Airflow inside Docker access Kafka?

**Answer**:

- Containers on same Docker network can communicate
- They use **service names** as hostnames
- Airflow connects to `kafka:29092` (not `localhost:9092`)
- From host machine, you use `localhost:9092`

**Question**: Where is my data stored?

**Answer**:

- **MySQL data**: Docker volume `mysql-db-volume` (persists after restart)
- **DAG files**: `./dags` folder (your machine → mounted in container)
- **Logs**: `./logs` folder (your machine → mounted in container)
- **Container data**: Deleted when you run `docker-compose down -v`

**Question**: How do changes to DAGs take effect?

**Answer**:

- Airflow watches `./dags` folder
- New/changed files detected automatically (30-60 seconds)
- No need to restart services
- Just save file → refresh Airflow UI

---

**Now you understand the complete architecture! 🎓**

Next: Read `REQUIREMENTS_EXPLAINED.md` for deep dive into how requirements.txt works.

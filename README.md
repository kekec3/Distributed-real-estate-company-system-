# Distributed Real Estate Company System

A scalable, distributed software system designed to handle real estate operations, property listings, user/agent management, and property transactions across distributed nodes. Built with high availability, fault tolerance, and modular service communication in mind.

---

## 📋 Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Running the System](#running-the-system)
- [API Overview](#api-overview)
- [Project Structure](#project-structure)
- [License](#license)

---

## 🔎 Overview

The **Distributed Real Estate Company System** models a multi-node real estate enterprise platform. It enables real estate agents, clients, and administrators to interact seamlessly with property databases, perform distributed searches, manage contracts/reservations, and synchronize real-time updates across decoupled services.

The system addresses core distributed systems challenges including concurrent access management, data consistency across nodes, service discovery, and message queuing for asynchronous event propagation.

---

## ✨ Key Features

- **Distributed Property Management:** Add, update, and search property listings across distributed storage nodes.
- **Role-Based Access Control (RBAC):** Distinct privileges for Clients, Agents, and System Administrators.
- **Distributed Search & Filtering:** Efficient queries by location, price range, property type, and availability.
- **Transaction & Reservation Workflow:** Concurrency-safe property booking and agreement handling.
- **Asynchronous Notifications:** Event-driven updates for price changes, status updates, and inquiry alerts.
- **Service Resilience & Fault Tolerance:** Graceful degradation and fallback mechanisms during node failure.

---

## 🏗 System Architecture

The architecture consists of decoupled components communicating via REST / gRPC and asynchronous messaging:

```text
                  +-----------------------+
                  |  API Gateway / Client |
                  +-----------+-----------+
                              |
       +----------------------+----------------------+
       |                      |                      |
+------v-------+      +-------v------+      +--------v-------+
| Auth Service |      | Real Estate  |      |  Transaction   |
|              |      | Service      |      |  & Booking     |
+------+-------+      +-------+------+      +--------+-------+
       |                      |                      |
       +----------------------+----------------------+
                              |
                     +--------v-------+
                     | Event Bus /    |
                     | Message Queue  |
                     +--------+-------+
                              |
                     +--------v-------+
                     | Notification   |
                     | Service        |
                     +----------------+
```

1. **API Gateway / Frontend:** Entry point handling routing, rate limiting, and client requests.
2. **Auth Service:** Manages user registration, JWT authentication, and access tokens.
3. **Real Estate / Property Service:** Core domain service managing property metadata, media, and search indexes.
4. **Transaction & Booking Service:** Handles client inquiries, scheduling, and contract states.
5. **Notification Service:** Listens to cluster events (e.g., updates, booking confirmation) and dispatches alerts.

---

## 🛠 Tech Stack

- **Backend / Core Services:** Python (Flask / FastAPI) / Java (Spring Boot) / Go *(adjust based on your setup)*
- **Database & Storage:** PostgreSQL / MySQL (Relational), Redis (Caching & Session management), MongoDB (Document store)
- **Messaging / Event Streaming:** RabbitMQ / Apache Kafka
- **Containerization & Orchestration:** Docker, Docker Compose, Kubernetes
- **Communication Protocols:** REST, gRPC, WebSockets

---

## ⚡ Prerequisites

Ensure you have the following installed locally before running the project:

- [Docker Engine](https://docs.docker.com/get-docker/) (`>= 20.10`)
- [Docker Compose](https://docs.docker.com/compose/install/) (`>= 2.0`)
- [Git](https://git-scm.com/)
- Programming language runtime (e.g., Python `3.10+`, Java `17+`, or Node.js `18+` depending on local deployment)

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/kekec3/Distributed-real-estate-company-system-.git
cd Distributed-real-estate-company-system-
```

### 2. Environment Setup
Copy the example environment file and update the parameters according to your environment:
```bash
cp .env.example .env
```

---

## ⚙️ Configuration

Key environment variables available in `.env`:

| Variable | Description | Default Value |
| :--- | :--- | :--- |
| `PORT` | API Gateway Port | `8080` |
| `DB_HOST` | Main Database Host | `localhost` |
| `DB_PORT` | Main Database Port | `5432` |
| `REDIS_HOST` | Redis Cache Host | `localhost` |
| `RABBITMQ_HOST` | Message Broker Host | `localhost` |
| `JWT_SECRET` | Secret key for JWT signing | `your_secret_key` |

---

## 🏃 Running the System

### Option A: Running with Docker Compose (Recommended)

To start all microservices, databases, and message brokers in detached mode:

```bash
docker-compose up -d --build
```

To view live logs across services:
```bash
docker-compose logs -f
```

To stop all running services:
```bash
docker-compose down
```

### Option B: Local Manual Run

1. Start required infrastructure services (Database, Redis, Message Queue):
   ```bash
   docker-compose up -d db redis rabbitmq
   ```
2. Start individual microservices from their respective directories:
   ```bash
   # Example for running a service
   cd services/property-service
   pip install -r requirements.txt
   python main.py
   ```

---

## 📡 API Overview

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/api/auth/register` | Register a new user | ❌ |
| `POST` | `/api/auth/login` | Authenticate & receive JWT token | ❌ |
| `GET` | `/api/properties` | Fetch property listings (filterable) | ❌ |
| `GET` | `/api/properties/:id` | Fetch property details by ID | ❌ |
| `POST` | `/api/properties` | Create a new real estate listing | ✅ (Agent) |
| `PUT` | `/api/properties/:id` | Update property metadata | ✅ (Agent) |
| `POST` | `/api/bookings` | Submit a property reservation request | ✅ (Client) |

---

## 📁 Project Structure

```text
Distributed-real-estate-company-system-/
├── config/                 # System-wide configuration files
├── docs/                   # System design documents & diagrams
├── services/               # Microservices modules
│   ├── auth-service/       # Authentication & user management
│   ├── property-service/   # Property management & search index
│   ├── booking-service/    # Transactions & reservations
│   └── notify-service/     # Event consumers & notifications
├── gateway/                # Reverse proxy / API Gateway configuration
├── docker-compose.yml      # Multi-container orchestration definition
├── .env.example            # Environment variables template
└── README.md               # Project documentation
```

---

## 📜 License

Distributed under the [MIT License](LICENSE). Feel free to modify and adapt for personal or academic projects.

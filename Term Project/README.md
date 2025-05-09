# CS408 Term Project Phase III Implementation

## Authors

- Mete Kerem Berk — 30933  
- Kaan Karahan — 30715  
- Efe Yağız San — 22521  

**Sabancı University — CS408 Spring 2025**

---

## Project Overview

This project simulates an environmental monitoring system using a **drone as an edge computing node**. It demonstrates TCP-based communication, real-time data aggregation, anomaly detection, GUI-based visualization, battery management, and dynamic sensor connection monitoring.

The system includes:

- **Sensor Nodes**: Simulate environmental data collection (temperature, humidity).
- **Drone Node**: Acts as an edge processor. Receives sensor data, performs local computation (averaging, anomaly detection), and forwards summarized data to the Central Server. It also maintains GUI-based logs, battery simulation, and configurable thresholds.
- **Central Server**: Collects and displays processed information in real time. Tracks anomalies, average data, and connection status of all sensors.

---

## File Structure

```
cs408/
├── sensor.py           # Headless sensor node with graceful shutdown
├── drone.py            # Drone edge node with GUI, aggregation, anomaly detection
├── central_server.py   # Central server GUI to display processed data
```

---

## How to Run the System

### 1. Start the Central Server (GUI)

```bash
python central_server.py --port 6000
```

- Opens a GUI window labeled **Central Server**.
- Listens on port 6000 for incoming data from the Drone.
- Displays all received messages.
- Shows a table of aggregated average temperature/humidity per sensor.
- Lists anomalies with timestamps and flags.
- Shows real-time connection **status** of each sensor (Connected/Disconnected).

---

### 2. Start the Drone Node (GUI)

```bash
python drone.py --port 5000 --central_ip 127.0.0.1 --central_port 6000
```

- Opens a GUI titled **Drone Edge Node**.
- Listens on port 5000 for sensor connections.
- Aggregates data using a rolling window of the last 5 readings.
- Detects anomalies based on **configurable thresholds** (default: temp < -10 or > 60 °C).
- Displays real-time sensor data and anomalies in separate tables.
- Logs all sensor events and connection changes.
- Includes:
  - **Battery input** to simulate varying battery levels
  - **Returning to base** state when battery < 20%, stops forwarding
  - Temperature threshold sliders for anomaly tuning
  - Disconnect handling for sensor nodes and forwarding sensor disconnection status to Central Server

---

### 3. Start a Sensor Node

```bash
python sensor.py --drone_ip 127.0.0.1 --drone_port 5000 --interval 2 --sensor_id sensor1
```

- Sends temperature and humidity data every 2 seconds.
- Sends its unique `sensor_id` with each reading.
- On manual interruption (Ctrl+C), it sends a `disconnect` message to the Drone.
- Automatically reconnects if disconnected.
- Logs connection status and sent data in the terminal.

---

## Expected Outcomes

| Component         | Behavior                                                                 |
|------------------|--------------------------------------------------------------------------|
| **Sensor Node**   | Sends periodic JSON with sensor ID, temperature, humidity, timestamp. Gracefully disconnects on termination. |
| **Drone Node**    | Aggregates last 5 readings per sensor, flags anomalies based on configurable thresholds, logs and forwards data unless battery < 20%. Handles sensor disconnects and forwards status. |
| **Central Server**| Displays forwarded JSON with sensor averages and anomalies. Updates sensor connection status in real time (Connected/Disconnected). |

---

## Phase III Features Summary

Dynamic **sensor connection status** detection and display  
**Disconnect message handling** on sensor exit  
**Battery level input** with threshold-based behavior  
**Configurable anomaly detection thresholds** via GUI sliders  
**Structured real-time tables** for sensor data and anomalies  
**Robust forwarding and logging** between system layers

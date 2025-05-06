# CS408 Term Project Phase II Implementation

## Authors

- Mete Kerem Berk — 30933  
- Kaan Karahan — 30715  
- Efe Yağız San — 22521  

**Sabancı University — CS408 Spring 2025**

---
## Project Overview

This project simulates an environmental monitoring system using a **drone as an edge computing node**. It demonstrates TCP-based communication, real-time data aggregation, anomaly detection, GUI-based visualization, and behavior under battery constraints.

The system includes:

- **Sensor Nodes**: Simulate environmental data collection (temperature, humidity).
- **Drone Node**: Acts as an edge processor. Receives sensor data, performs local computation (averaging, anomaly detection), and forwards summarized data to the Central Server.
- **Central Server**: Collects and displays processed information, including anomalies.

---

## File Structure

```
cs408/
├── sensor.py           # Headless sensor node
├── drone.py            # Drone edge node with GUI and logic
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
- Displays all received messages and logs anomalies.

---

### 2. Start the Drone Node (GUI)

```bash
python drone.py --port 5000 --central_ip 127.0.0.1 --central_port 6000
```

- Opens a GUI titled **Drone Edge Node**.
- Listens on port 5000 for sensor connections.
- Aggregates data, detects anomalies (temperature > 100°C), and forwards summaries to the Central Server.
- Includes a button to simulate battery drain. If battery drops below 20%, the drone enters **Returning to base** mode and stops forwarding data.

---

### 3. Start a Sensor Node

```bash
python sensor.py --drone_ip 127.0.0.1 --drone_port 5000 --interval 2 --sensor_id sensor1
```

- Sends temperature and humidity data every 2 seconds.
- Automatically reconnects if disconnected.
- Logs connection status and sent data in the terminal.

---

## Expected Outcomes

| Component        | Behavior                                                                 |
|------------------|--------------------------------------------------------------------------|
| **Sensor Node**   | Sends periodic JSON with sensor ID, temperature, humidity, timestamp.   |
| **Drone Node**    | Aggregates last 5 readings, flags anomalies (temperature > 100°C), logs and forwards data unless battery < 20%. |
| **Central Server**| Displays forwarded JSON with averages and anomalies in GUI.             |

---

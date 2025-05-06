import socket
import time
import argparse
import json
from datetime import datetime


def create_sensor_data(sensor_id):
    return json.dumps({
        "sensor_id": sensor_id,
        "temperature": round(20 + 5 * (0.5 - time.time() % 1), 2),
        "humidity": round(50 + 10 * (0.5 - time.time() % 1), 2),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })


def run_sensor(drone_ip, drone_port, interval, sensor_id):
    while True:
        try:
            print(f"[INFO] Connecting to Drone at {drone_ip}:{drone_port}...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((drone_ip, drone_port))
                print("[SUCCESS] Connected to Drone.")
                while True:
                    data = create_sensor_data(sensor_id)
                    s.sendall(data.encode())
                    print(f"[SENT] {data}")
                    time.sleep(interval)
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}. Retrying in 5s...")
            time.sleep(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--drone_ip", default="127.0.0.1")
    parser.add_argument("--drone_port", type=int, default=5000)
    parser.add_argument("--interval", type=int, default=2)
    parser.add_argument("--sensor_id", default="sensor1")
    args = parser.parse_args()
    run_sensor(args.drone_ip, args.drone_port, args.interval, args.sensor_id)

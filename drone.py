import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk
import argparse
import json
import time

battery_level = 100
battery_threshold = 20
is_returning_to_base = False

def handle_sensor(client_socket, address, forward_func, gui_log, update_battery_display, update_data_view, add_anomaly, get_threshold):
    global battery_level, battery_threshold, is_returning_to_base

    with client_socket:
        gui_log(f"Sensor connected from {address}")
        sensor_id = None
        sensor_data_list = []

        while True:
            try:
                if battery_level < battery_threshold:
                    is_returning_to_base = True
                    gui_log("[BATTERY] Battery too low. Returning to base. Closing sensor connection.")
                    break

                data = client_socket.recv(1024)
                if not data:
                    break

                decoded = data.decode()
                sensor_data = json.loads(decoded)

                if "status" in sensor_data and sensor_data["status"] == "Disconnected":
                    status_update = json.dumps({
                        "sensor_id": sensor_data["sensor_id"],
                        "status": "Disconnected"
                    })
                    forward_func(status_update)
                    gui_log(f"[INFO] Sensor {sensor_data['sensor_id']} reported disconnection.")
                    break

                if not sensor_id:
                    sensor_id = sensor_data.get("sensor_id", "unknown")

                if sensor_id and len(sensor_data_list) == 0:
                    status_update = json.dumps({
                        "sensor_id": sensor_id,
                        "status": "Connected"
                    })
                    forward_func(status_update)
                    gui_log(f"[INFO] Sensor {sensor_id} reconnected.")

                sensor_data_list.append(sensor_data)

                avg_temp = round(sum(d.get("temperature", 0) for d in sensor_data_list[-5:]) / min(len(sensor_data_list), 5), 2)
                avg_hum = round(sum(d.get("humidity", 0) for d in sensor_data_list[-5:]) / min(len(sensor_data_list), 5), 2)

                anomalies = []
                temp = sensor_data.get("temperature", 0)
                tmin, tmax = get_threshold()
                if temp < tmin or temp > tmax:
                    anomalies.append(sensor_data)
                    add_anomaly(sensor_data)

                drone_output = json.dumps({
                    "sensor_id": sensor_id,
                    "avg_temperature": avg_temp,
                    "avg_humidity": avg_hum,
                    "anomalies": anomalies
                })

                update_data_view(sensor_data, avg_temp, avg_hum, is_anomaly=bool(anomalies))
                gui_log(f"Received: {decoded}")
                gui_log(f"Processed → {drone_output}")

                forward_func(drone_output)
                update_battery_display(battery_level)

            except Exception as e:
                gui_log(f"[ERROR] {e}")
                break

        gui_log(f"Sensor disconnected from {address}")

def start_sensor_server(drone_port, forward_func, gui_log, update_battery_display, update_data_view, add_anomaly, get_threshold):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", drone_port))
    server_socket.listen()
    gui_log(f"[INFO] Drone listening on port {drone_port}")
    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(
            target=handle_sensor,
            args=(client_socket, addr, forward_func, gui_log, update_battery_display, update_data_view, add_anomaly, get_threshold),
            daemon=True
        ).start()

def create_gui():
    root = tk.Tk()
    root.title("Drone Edge Node")

    battery_label = tk.Label(root, text="Battery: 100%")
    battery_label.pack()

    status_label = tk.Label(root, text="Status: Active", fg="green")
    status_label.pack()

    tk.Label(root, text="📊 Real-Time Sensor Data").pack()
    data_table = ttk.Treeview(root, columns=("Time", "Sensor", "Temp", "Hum"), show="headings", height=5)
    for col in ("Time", "Sensor", "Temp", "Hum"):
        data_table.heading(col, text=col)
    data_table.pack(pady=5)

    tk.Label(root, text="⚠️ Anomalies").pack()
    anomaly_table = ttk.Treeview(root, columns=("Time", "Sensor", "Temp", "Hum"), show="headings", height=5)
    for col in ("Time", "Sensor", "Temp", "Hum"):
        anomaly_table.heading(col, text=col)
    anomaly_table.pack(pady=5)

    tk.Label(root, text="📜 Log Panel").pack()
    log_text = scrolledtext.ScrolledText(root, width=80, height=10)
    log_text.pack()

    tk.Label(root, text="Set Temperature Threshold (min - max):").pack()
    threshold_min = tk.Scale(root, from_=-50, to=50, orient=tk.HORIZONTAL)
    threshold_min.set(0)
    threshold_min.pack()
    threshold_max = tk.Scale(root, from_=50, to=150, orient=tk.HORIZONTAL)
    threshold_max.set(100)
    threshold_max.pack()

    battery_entry_label = tk.Label(root, text="Set Battery Level (%):")
    battery_entry_label.pack()
    battery_entry = tk.Entry(root)
    battery_entry.pack()

    def gui_log(msg):
        log_text.insert(tk.END, msg + "\n")
        log_text.see(tk.END)

    def update_battery_display(level):
        battery_label.config(text=f"Battery: {level}%")
        status = "Returning to base" if level < battery_threshold else "Active"
        status_label.config(text=f"Status: {status}", fg="red" if level < battery_threshold else "green")

    def update_data_view(data, avg_temp, avg_hum, is_anomaly=False):
        if "timestamp" in data and "sensor_id" in data:
            values = (data["timestamp"], data["sensor_id"], data["temperature"], data["humidity"])
            data_table.insert("", 0, values=values)
            if len(data_table.get_children()) > 10:
                data_table.delete(data_table.get_children()[-1])

    def add_anomaly(data):
        if "timestamp" in data and "sensor_id" in data:
            values = (data["timestamp"], data["sensor_id"], data["temperature"], data["humidity"])
            anomaly_table.insert("", 0, values=values)
            if len(anomaly_table.get_children()) > 10:
                anomaly_table.delete(anomaly_table.get_children()[-1])

    def set_battery():
        global battery_level, is_returning_to_base
        try:
            level = int(battery_entry.get())
            if 0 <= level <= 100:
                battery_level = level
                update_battery_display(level)
                if is_returning_to_base and battery_level >= battery_threshold:
                    is_returning_to_base = False
                    gui_log("[BATTERY] Battery restored. Ready to reconnect sensors.")
            else:
                gui_log("[WARNING] Battery level must be between 0 and 100.")
        except ValueError:
            gui_log("[ERROR] Invalid input. Please enter an integer.")

    battery_button = tk.Button(root, text="Set Battery Level", command=set_battery)
    battery_button.pack()

    def get_threshold():
        return threshold_min.get(), threshold_max.get()

    return root, gui_log, update_battery_display, update_data_view, add_anomaly, get_threshold

def start_forwarder(central_ip, central_port, gui_log):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((central_ip, central_port))
        gui_log(f"[CONNECTED] to Central Server at {central_ip}:{central_port}")
    except Exception as e:
        gui_log(f"[ERROR] Could not connect to Central Server: {e}")
        return lambda data: None

    def forward(data):
        try:
            s.sendall(data.encode())
        except Exception as e:
            gui_log(f"[FORWARD ERROR] {e}")

    return forward

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--central_ip", default="127.0.0.1")
    parser.add_argument("--central_port", type=int, default=6000)
    args = parser.parse_args()

    root, gui_log, update_battery_display, update_data_view, add_anomaly, get_threshold = create_gui()
    forward_func = start_forwarder(args.central_ip, args.central_port, gui_log)

    threading.Thread(
        target=start_sensor_server,
        args=(args.port, forward_func, gui_log, update_battery_display, update_data_view, add_anomaly, get_threshold),
        daemon=True
    ).start()

    root.mainloop()

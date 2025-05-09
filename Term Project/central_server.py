import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk
import argparse
import json
from collections import defaultdict

sensor_data_store = defaultdict(lambda: {"temps": [], "hums": []})
sensor_table_rows = {}

def handle_client(conn, addr, gui_log, update_table, log_anomaly):
    gui_log(f"Drone connected from {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            decoded = data.decode()
            try:
                parsed = json.loads(decoded)
                gui_log(f"[RECEIVED] {decoded}")
                if "avg_temperature" in parsed and "avg_humidity" in parsed:
                    update_table(parsed)
                elif "status" in parsed and "sensor_id" in parsed:
                    update_table(parsed)
                if parsed.get("anomalies"):
                    for a in parsed["anomalies"]:
                        log_anomaly(a)
            except json.JSONDecodeError:
                gui_log(f"[ERROR] Failed to decode JSON: {decoded}")
            except Exception as e:
                gui_log(f"[ERROR] Drone connection error: {e}")
    finally:
        conn.close()
        gui_log(f"Drone disconnected from {addr}")

def start_server(port, gui_log, update_table, log_anomaly):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("", port))
    server.listen()
    gui_log(f"[INFO] Central Server listening on port {port}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr, gui_log, update_table, log_anomaly), daemon=True).start()

def create_gui():
    root = tk.Tk()
    root.title("Central Server")

    # Aggregated Sensor Data Table
    tk.Label(root, text="📊 Aggregated Sensor Averages").pack()
    table_frame = tk.Frame(root)
    table_frame.pack(pady=5, fill="both", expand=True)

    sensor_table = ttk.Treeview(table_frame, columns=("Sensor ID", "Avg Temp", "Avg Hum", "Status"), show="headings")
    for col in ("Sensor ID", "Avg Temp", "Avg Hum", "Status"):
        sensor_table.heading(col, text=col)
    sensor_table.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=sensor_table.yview)
    scrollbar.pack(side="right", fill="y")
    sensor_table.configure(yscrollcommand=scrollbar.set)

    # Anomaly Table
    tk.Label(root, text="⚠️ Anomalies from Drones").pack()
    anomaly_table = ttk.Treeview(root, columns=("Time", "Sensor", "Temp", "Hum"), show="headings", height=5)
    for col in ("Time", "Sensor", "Temp", "Hum"):
        anomaly_table.heading(col, text=col)
    anomaly_table.pack(pady=5)

    # Log Output
    tk.Label(root, text="📜 Message Log").pack()
    log_text = scrolledtext.ScrolledText(root, width=80, height=10)
    log_text.pack()

    def gui_log(msg):
        log_text.insert(tk.END, msg + "\n")
        log_text.see(tk.END)

    def update_table(parsed):
        anomalies = parsed.get("anomalies", [])
        sensor_id = parsed.get("sensor_id")

        if not sensor_id and anomalies:
            sensor_id = anomalies[0].get("sensor_id")

        if not sensor_id:
            gui_log("[WARNING] No sensor_id found in data.")
            return

        avg_temp = parsed.get("avg_temperature", 0)
        avg_hum = parsed.get("avg_humidity", 0)
        status = parsed.get("status", "Connected")

        if "avg_temperature" in parsed and "avg_humidity" in parsed:
            store = sensor_data_store[sensor_id]
            store["temps"].append(avg_temp)
            store["hums"].append(avg_hum)
            avg_temp_total = round(sum(store["temps"]) / len(store["temps"]), 2)
            avg_hum_total = round(sum(store["hums"]) / len(store["hums"]), 2)
        else:
            avg_temp_total = ""
            avg_hum_total = ""

        if sensor_id in sensor_table_rows:
            sensor_table.item(sensor_table_rows[sensor_id], values=(sensor_id, avg_temp_total, avg_hum_total, status))
        else:
            item = sensor_table.insert("", "end", values=(sensor_id, avg_temp_total, avg_hum_total, status))
            sensor_table_rows[sensor_id] = item

    def log_anomaly(a):
        if "timestamp" in a and "sensor_id" in a:
            values = (a["timestamp"], a["sensor_id"], a["temperature"], a["humidity"])
            anomaly_table.insert("", 0, values=values)
            if len(anomaly_table.get_children()) > 10:
                anomaly_table.delete(anomaly_table.get_children()[-1])

    return root, gui_log, update_table, log_anomaly

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=6000)
    args = parser.parse_args()

    root, gui_log, update_table, log_anomaly = create_gui()
    threading.Thread(target=start_server, args=(args.port, gui_log, update_table, log_anomaly), daemon=True).start()
    root.mainloop()

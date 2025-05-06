import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import json
import argparse

class DroneServer:
    def __init__(self, port, central_ip, central_port):
        self.port = port
        self.central_ip = central_ip
        self.central_port = central_port
        self.central_socket = None

        self.root = tk.Tk()
        self.root.title("Drone GUI")

        self.log_area = scrolledtext.ScrolledText(self.root, width=80, height=20)
        self.log_area.pack()

        threading.Thread(target=self.start_server, daemon=True).start()
        self.connect_to_central()
        self.root.mainloop()

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def connect_to_central(self):
        try:
            self.central_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.central_socket.connect((self.central_ip, self.central_port))
            self.log(f"[INFO] Connected to Central Server at {self.central_ip}:{self.central_port}")
        except Exception as e:
            self.log(f"[ERROR] Could not connect to Central Server: {e}")
            self.central_socket = None

    def forward_to_central(self, data):
        if self.central_socket:
            try:
                self.central_socket.sendall(data.encode())
                self.log("[FORWARDED] Data sent to Central Server")
            except Exception as e:
                self.log(f"[ERROR] Failed to send to Central Server: {e}")
                self.central_socket = None

    def handle_client(self, conn, addr):
        self.log(f"[INFO] Sensor connected from {addr}")
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                decoded = data.decode()
                self.log(f"[RECEIVED] {decoded}")
                self.forward_to_central(decoded)
        except Exception as e:
            self.log(f"[ERROR] Sensor connection error: {e}")
        finally:
            conn.close()
            self.log(f"[INFO] Sensor disconnected from {addr}")

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", self.port))
            s.listen()
            self.log(f"[INFO] Drone Server listening on port {self.port}")

            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True, help="Port to listen for sensors")
    parser.add_argument("--central_ip", type=str, required=True, help="Central server IP")
    parser.add_argument("--central_port", type=int, required=True, help="Central server port")
    args = parser.parse_args()

    DroneServer(args.port, args.central_ip, args.central_port)
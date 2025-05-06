import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import argparse


def start_server(port, gui_log):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", port))
    server_socket.listen()
    gui_log(f"[INFO] Central Server listening on port {port}")
    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, addr, gui_log)).start()

def handle_client(client_socket, address, gui_log):
    with client_socket:
        gui_log(f"[INFO] Drone connected from {address}")
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                gui_log(f"[RECEIVED] {data.decode()}")
            except Exception as e:
                gui_log(f"[ERROR] {e}")
                break
        gui_log(f"[INFO] Drone disconnected from {address}")

def create_gui():
    root = tk.Tk()
    root.title("Central Server")

    log_text = scrolledtext.ScrolledText(root, width=80, height=20)
    log_text.pack()

    def gui_log(msg):
        log_text.insert(tk.END, msg + "\n")
        log_text.see(tk.END)

    return root, gui_log

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=6000)
    args = parser.parse_args()

    root, gui_log = create_gui()
    threading.Thread(target=start_server, args=(args.port, gui_log), daemon=True).start()
    root.mainloop()

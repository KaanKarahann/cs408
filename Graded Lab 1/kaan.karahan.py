#Made by Kaan Karahan
#date: 07/03/2025
import tkinter as tk
import socket
import re 
#re is imported to use regular expressions #handles the invalid literal for int() with base 10: 'Your token is xxxx' error

# Create the main window
root = tk.Tk()
root.title("kaan.karahan client application")

# Function to handle connect button click
def connect():
    try:
        ip = ip_entry.get()
        port = int(port_entry.get())
        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        log_message("Connected to server")
    except Exception as e:
        log_message(f"Connection failed: {e}")

# Function to handle submit button click
def submit():
    try:
        username = username_entry.get().lower()
        client_socket.sendall(username.encode())
        token_message = client_socket.recv(1024).decode()
        log_message(f"Received token message: {token_message}")

        # Extract the numeric token from the message
        token = int(re.search(r'\d+', token_message).group())
        log_message(f"Extracted token: {token}")

        max_ascii = max(ord(char) for char in username)
        result = max_ascii * token
        client_socket.sendall(str(result).encode())
        log_message(f"Sent result: {result}")

        response = client_socket.recv(1024).decode()
        log_message(f"Server response: {response}")
        client_socket.close()
    except Exception as e:
        log_message(f"Error: {e}")

# Function to log messages to the output box
def log_message(message):
    output_box.config(state=tk.NORMAL)
    output_box.insert(tk.END, message + "\n")
    output_box.config(state=tk.DISABLED)

# Server info frame
server_frame = tk.LabelFrame(root, text="Server Info")
server_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

# IP Address and Port entries
tk.Label(server_frame, text="IP Address:").grid(row=0, column=0, padx=10, pady=5)
ip_entry = tk.Entry(server_frame)
ip_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(server_frame, text="Puzzle Port:").grid(row=1, column=0, padx=10, pady=5)
port_entry = tk.Entry(server_frame)
port_entry.grid(row=1, column=1, padx=10, pady=5)

# Connect button
connect_btn = tk.Button(server_frame, text="Connect", command=connect)
connect_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Log frame
log_frame = tk.LabelFrame(root, text="Log")
log_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

# Output box (read-only)
output_box = tk.Text(log_frame, width=50, height=20, state=tk.DISABLED)
output_box.grid(row=0, column=0, padx=10, pady=10)

# Data entry frame
data_frame = tk.LabelFrame(root, text="Enter your username")
data_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="n")

# Username entry
tk.Label(data_frame, text="Username:").grid(row=0, column=0, padx=10, pady=5)
username_entry = tk.Entry(data_frame)
username_entry.grid(row=0, column=1, padx=10, pady=5)

# Submit button
submit_btn = tk.Button(data_frame, text="Submit", command=submit)
submit_btn.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# Run the Tkinter event loop
root.mainloop()
import json
import socket


def notify(ip: str, port: int, msg: dict):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(2)
            s.connect((ip, port))
            s.sendall(json.dumps(msg).encode())
        except socket.timeout:
            print(f"Notification of client {ip}:{port} failed!")

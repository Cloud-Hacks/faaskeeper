import json
import logging
import socket
from abc import ABC, abstractmethod
from typing import Dict

import boto3


class ClientChannel(ABC):
    @abstractmethod
    def notify(self, session_id: str, event: str, write_event: dict, ret: dict):
        pass


# FIXME: replace with proper deserialization
def get_object(obj: dict):
    return next(iter(obj.values()))


class ClientChannelTCP(ClientChannel):
    def __init__(self):
        self._sockets = {}

    def _get_socket(self, user: str, write_event: dict):

        sock = self._sockets.get(user, None)

        if sock is None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.settimeout(2)
                source_ip = get_object(write_event["sourceIP"])
                source_port = int(get_object(write_event["sourcePort"]))
                sock.connect((source_ip, source_port))
                logging.info(f"Connected to {source_ip}:{source_port}")

                self._sockets[user] = sock
            except socket.timeout:
                logging.error(f"Connection to client {source_ip}:{source_port} failed!")
            except OSError as e:
                logging.error(
                    f"Connection to client {source_ip}:{source_port} failed! Reason {e.strerror}"
                )

        return sock

    def notify(self, user: str, event: str, write_event: dict, ret: dict):
        sock = self._get_socket(user, write_event)
        if sock is None:
            logging.error(f"Notification of client {user} failed!")
            return

        try:
            sock.sendall(
                json.dumps(
                    {**ret, "event": event}
                    # get_object(write_event["timestamp"])}
                ).encode()
            )
        except socket.timeout:
            logging.error(f"Notification of client {user} failed!")

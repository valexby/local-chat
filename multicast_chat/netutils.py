import netifaces as ni
import socket
import threading
import struct
from threading import Thread
from select import select
import pickle

CHAT_PORT = 13998
MULTICAST_ADDRESS = '224.1.2.3'
RECV_TIMEOUT = 0.5

def get_ifaces_info():
    interfaces = {}
    for interface in ni.interfaces():
        try:
            interface_info = ni.ifaddresses(interface)[ni.AF_INET][0]
            if 'broadcast' in interface_info:
                interfaces[interface] = interface_info
        except KeyError:
            pass
    return interfaces


class BroadcastClient:
    def __init__(self, interface, callback, port=CHAT_PORT, address=MULTICAST_ADDRESS):
        self.ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
        self.address = address
        self.port = port
        self.callback = callback
        self._sock = self._open_multicast_socket()
        self._stop_event = threading.Event()
        self._consuming_thread = Thread(target=self._blocking_consume,
                                        name='CommunicationThread')

    def _open_multicast_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        ttl = struct.pack('b', 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        mreq = struct.pack('4sL', socket.inet_aton(self.address), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.bind(('', self.port))
        return sock

    def start(self):
        """Start thread for blocking message consuming."""
        self._stop_event.clear()
        self._consuming_thread.start()

    def stop(self):
        """Stop thread for blocking message consuming."""
        self._stop_event.set()
        self._consuming_thread.join()

    def _blocking_consume(self):
        while not self._stop_event.is_set():
            readable, *_ = select(
                (self._sock, ), tuple(), tuple(), RECV_TIMEOUT)
            if readable:
                bin_message, (sender, _) = self._sock.recvfrom(self.port)
                if sender == self.ip:
                    continue
                message = pickle.loads(bin_message)
                self.callback(sender, message)

    def send_msg(self, message):
        bin_message = pickle.dumps(message)
        self._sock.sendto(bin_message, (self.address, self.port))

    def close(self):
        self._sock.close()

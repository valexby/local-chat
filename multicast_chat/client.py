#!/usr/bin/env python3
import time
import logging
import netutils

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s')
LOG = logging.getLogger(__name__)

class ChatClient(object):
    def __init__(self):
        super().__init__()
        self._connected_clients = set()
        self._messages = []
        self._ban_list = set()
        interfaces = netutils.get_ifaces_info()
        iface = choose_interface_dialog(list(interfaces.keys()))
        self._msg_client = netutils.BroadcastClient(iface, self._recieve_msg)
        print_message('System', 'Starting local chat using {} interface. Your '
                         'IP address is `{}`'.format(iface, interfaces[iface]['addr']))

    def _recieve_msg(self, sender, message):
        if sender in self._ban_list:
            return
        if message.startswith('-msg '):
            message = message[5:]
            print_message(sender, message)
        elif message == '-connect':
            self._connected_clients.add(sender)
            self._msg_client.send_msg('-connect-reply')
            print_message('System', 'Client `{}` has become online'.format(sender))
        elif message == '-connect-reply':
            self._connected_clients.add(sender)
        elif message == '-disconnect':
            self._connected_clients.discard(sender)
            print_message('System', 'Client `{}` has gone offline'.format(sender))

    def run(self):
        try:
            self.start()
            while True:
                command = input()
                if command.strip() == '-list':
                    for client in self._connected_clients:
                        print("==> {}".format(client))
                elif command.startswith('-ban '):
                    banned = command[5:].strip()
                    self._ban_list.add(banned)
                    self._connected_clients.discard(banned)
                else:
                    self._msg_client.send_msg("-msg " + command)
                    print_message('You', command)

        except KeyboardInterrupt:
            self.stop()


    def start(self):
        self._msg_client.start()
        self._msg_client.send_msg('-connect')

    def stop(self):
        self._msg_client.send_msg('-disconnect')
        self._msg_client.stop()


def print_message(source, message):
    cur_time = time.strftime('%H:%M:%S')
    text = '{} {} ==> {}'.format(source, cur_time, message)
    print(text)


def choose_interface_dialog(interfaces):
    while True:
        for i, interface in enumerate(interfaces):
            print("{}) {}".format(i + 1, interface))
        choosen = input("Choose interface: ")
        if choosen.isdecimal():
            choosen = int(choosen)
            if choosen >= 1 and choosen <= len(interfaces):
                break
    return interfaces[choosen - 1]


def main():
    chat = ChatClient()
    chat.run()


if __name__ == '__main__':
    main()

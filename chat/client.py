import time

from chat import netutils


class ChatClient(object):
    def __init__(self):
        super().__init__()
        self._connected_clients = set()
        self._messages = []
        interfaces = netutils.get_ifaces_info()
        iface = choose_interface_dialog(list(interfaces.keys()))
        self._msg_client = netutils.BroadcastClient(iface, self._recieve_msg)
        print_message('System', 'Starting local chat using `%s` interface. Your '
                         'IP address is `%s`' % (iface, interfaces[iface]['addr']))

    def _recieve_msg(self, sender, message):
        if message.startswith('-msg '):
            message = message[5:]
            print_message(sender, message)
        elif message.startswith('-connect '):
            self._connected_clients.add(sender)
            self._msg_client.send_msg('-connect-reply ')
            print_message('System', 'Client `%s` has become online' % sender)
        elif message.startswith('-connect-reply '):
            self._connected_clients.add(sender)
        elif message.startswith('-disconnect '):
            self._connected_clients.discard(sender)
            print_message('System', 'Client `%s` has gone offline' % sender)

    def run(self):
        try:
            self._start_program_logics()
            while True:
                command = input()
                if command.startswith('-msg ') or not command.startswith('-'):
                    self._msg_client.send_msg(command)
                    print_message('You', command[5:])
                if command.startswith('-list '):
                    for client in self._connected_clients:
                        print("==> {}".format(client))

        except KeyboardInterrupt:
            self.stop()


    def _start_program_logics(self):
        self._msg_client.start()
        self._msg_client.send_msg('\\connect ')

    def stop(self):
        self._msg_client.send_msg('\\disconnect ')
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

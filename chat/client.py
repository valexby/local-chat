from chat.cli.interface import ChatInterface
from chat import netutils


class ChatClient(ChatInterface):
    def __init__(self):
        super().__init__()
        interfaces = netutils.get_ifaces_info()
        iface = choose_interface_dialog(list(interfaces.keys()))
        self._msg_client = netutils.BroadcastClient(iface, self._recieve_msg)
        self.add_message('System', 'Starting local chat using `%s` interface. Your '
                         'IP address is `%s`' % (iface, interfaces[iface]['addr']))

    def _recieve_msg(self, sender, message):
        if message.startswith('\\msg '):
            message = message[5:]
            self.add_message(sender, message)
        elif message.startswith('\\connect '):
            self.add_client(sender)
            self._msg_client.send_msg('\\connect-reply ')
            self.add_message('System', 'Client `%s` has become online' % sender)
        elif message.startswith('\\connect-reply '):
            self.add_client(sender)
        elif message.startswith('\\disconnect '):
            self.remove_client(sender)
            self.add_message('System', 'Client `%s` has gone offline' % sender)

    def _start_program_logics(self):
        self._msg_client.start()
        self._msg_client.send_msg('\\connect ')

    def _stop_program_logics(self):
        self._msg_client.send_msg('\\disconnect ')
        self._msg_client.stop()


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

import time
import urwid

from chat.cli.commands import CommandDispatcher


class _PatchedEdit(urwid.Edit):
    _metaclass_ = urwid.signals.MetaSignals
    signals = ['command_entered']

    def keypress(self, size, key):
        if key == 'enter':
            urwid.emit_signal(
                self, 'command_entered', self, self.get_edit_text())
            super().set_edit_text('')
            return
        elif key == 'esc':
            super().set_edit_text('')
            return
        urwid.Edit.keypress(self, size, key)


class ChatInterface(object):
    _palette = [
        ('body', 'black', 'light gray', 'standout'),
        ('border', 'black', 'dark blue'),
        ('shadow', 'white', 'black'),
        ('selectable', 'black', 'dark cyan'),
        ('focus', 'white', 'dark blue', 'bold'),
        ('focustext', 'light gray', 'dark blue'),
    ]

    def __init__(self):
        self._messages = []
        self._connected_clients = set()
        self._cmd_dispatcher = CommandDispatcher(self)

    def _command_entered(self, edit, text):
        if not text.startswith('\\'):
            text = '\\msg ' + text
        text = text[1:]
        self._cmd_dispatcher.onecmd(text)

    def run(self):
        try:
            self._start_program_logics()
            while True:
                command = input()
                if not command.startswith('\\'):
                    command = '\\msg ' + command
                command = command[1:]
                self._cmd_dispatcher.onecmd(command)
        except KeyboardInterrupt:
            pass
            # self._stop_program_logics()

    def stop(self):
        self._stop_program_logics()

    def print_peers(self):
        for client in self._connected_clients:
            print("==> {}".format(client))

    def _start_program_logics(self):
        pass

    def _stop_program_logics(self):
        pass

    def add_message(self, source, message):
        cur_time = time.strftime('%H:%M:%S')
        text = '{} {} ==> {}'.format(source, cur_time, message)
        print(text)

    def add_client(self, client):
        self._connected_clients.add(client)

    def remove_client(self, client):
        self._connected_clients.discard(client)

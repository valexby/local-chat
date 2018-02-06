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
        # self._main_loop = urwid.MainLoop(self._init_interface(), self._palette)
        self._cmd_dispatcher = CommandDispatcher(self)

    def _init_interface(self):
        """Returns main interface frame."""
        header = urwid.LineBox(
            urwid.Text('Local Chat by Yury Zaitsau, 2017', align=urwid.CENTER))
        body = urwid.Columns([
            (urwid.LineBox(urwid.ListBox(self._messages), title="Chat history")),
            ('fixed', 20, urwid.LineBox(urwid.ListBox(self._connected_clients), title="Clients online")),
        ])
        edit = _PatchedEdit(caption=' command: ', multiline=True)
        urwid.connect_signal(edit, 'command_entered', self._command_entered)
        footer = urwid.LineBox(edit, title='Command line')
        frame = urwid.Frame(body, header, footer)
        frame.focus_position = 'footer'
        return frame

    def _command_entered(self, edit, text):
        if not text.startswith('\\'):
            text = '\\msg ' + text
        text = text[1:]
        self._cmd_dispatcher.onecmd(text)

    def run(self):
        try:
            # self._start_program_logics()
            # self._main_loop.run()
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

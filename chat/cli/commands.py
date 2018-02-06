import cmd


class CommandDispatcherBase(cmd.Cmd):
    """Base class for mapping app command names to command functionality.

       If you want to add a new command to app just add new method like
       do_<command_name>(self, line). Line contains string with command arguments.
       Note that command names are case-sensitive.
    """
    def __init__(self, interface):
        super().__init__()
        self._interface = interface

    def emptyline(self):
        pass

    def default(self, line):
        txt = 'Command not recognized: `%s`.' % line
        self._interface.add_message('System', txt)


class CommandDispatcher(CommandDispatcherBase):
    def do_msg(self, line):
        message = '\msg %s' % line
        self._interface._msg_client.send_msg(message)
        self._interface.add_message('You', line)

    def do_list(self, _):
        self._interface.print_peers()

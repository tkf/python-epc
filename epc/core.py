import logging


def _get_logger():
    """
    Generate a logger with a stream handler.
    """
    logger = logging.getLogger('epc')
    hndlr = logging.StreamHandler()
    hndlr.setLevel(logging.INFO)
    hndlr.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    logger.addHandler(hndlr)
    return logger
logger = _get_logger()


class EPCDispacher:

    # This class will be mixed with `SocketServer.TCPServer`,
    # which is an old style class.

    # see also: SimpleXMLRPCServer.SimpleXMLRPCDispatcher

    def __init__(self):
        self.funcs = {}
        self.instance = None

    def register_instance(self, instance, allow_dotted_names=False):
        self.instance = instance
        self.allow_dotted_names = allow_dotted_names
        raise NotImplementedError

    def register_function(self, function, name=None):
        """
        Register function to be called from EPC client.

        :type  function: callable
        :arg   function: Function to publish.
        :type      name: str
        :arg       name: Name by which function is published.

        This method returns the given `function` as-is, so that you
        can use it as a decorator.

        """
        if name is None:
            name = function.__name__
        self.funcs[name] = function
        return function


class EPCCore(EPCDispacher):

    """
    Core methods shared by `EPCServer` and `EPCClient`.
    """

    logger = logger

    def __init__(self, debugger):
        EPCDispacher.__init__(self)
        self.set_debugger(debugger)

    def set_debugger(self, debugger):
        """
        Set debugger to run when an error occurs in published method.

        You can also set debugger by passing `debugger` argument to
        the class constructor.

        :type debugger: {'pdb', 'ipdb', None}
        :arg  debugger: type of debugger.

        """
        if debugger == 'pdb':
            import pdb
            self.debugger = pdb
        elif debugger == 'ipdb':
            import ipdb
            self.debugger = ipdb
        else:
            self.debugger = debugger

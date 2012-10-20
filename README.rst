EPC (RPC stack for Emacs Lisp) server for Python
================================================

Install
-------

To install python-epc and its dependency sexpdata_, run the following
command.::

   pip install epc

.. _sexpdata: https://github.com/tkf/sexpdata


Usage
-----

Save the following code as ``my-server.py``.
(You can find the same code at the bottom of ``epc/server.py``)::

   from epc.server import EPCServer

   def echo_server(address='localhost', port=0):
       server = EPCServer((address, port))
       def echo(*a):
           return a
       server.register_function(echo)
       return server

   if __name__ == '__main__':
       server = echo_server()
       server.print_port()
       server.serve_forever()


And then run the following code from Emacs.
This is a stripped version of client.el included in python-epc
repository.::

   (require 'epc)

   (defvar my-epc (epc:start-epc "python" '("my-server.py")))

   (deferred:$
     (epc:call-deferred my-epc 'echo '(10))
     (deferred:nextc it
       (lambda (x) (message "Return : %S" x))))

   (message "Return : %S" (epc:call-sync my-epc 'echo '(10 40)))


If you have carton_ installed, you can run the above sample by
simply typing the following commands::

   make install     # install EPC in a separated environment
   make run-sample  # run client.el

.. _carton: https://github.com/rejeep/carton


Links
-----

.. Host documentation at Read the Docs (but not now).
   * `Documentaions (at Read the Docs) <http://python-epc.readthedocs.org/>`_

* `Repository (at GitHub) <https://github.com/tkf/python-epc>`_
* `Issue tracker (at GitHub) <https://github.com/tkf/python-epc/issues>`_
* `PyPI <http://pypi.python.org/pypi/python-epc>`_

.. Run test on Travis CI at some point (but not now).
   * `Travis CI <https://travis-ci.org/#!/tkf/python-epc>`_

* `kiwanami/emacs-epc <https://github.com/kiwanami/emacs-epc>`_
  (Client and server implementation in Emacs Lisp and Perl.)

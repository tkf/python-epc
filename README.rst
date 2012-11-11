EPC (RPC stack for Emacs Lisp) server for Python
================================================

Links:

* `Documentation <http://python-epc.readthedocs.org/>`_ (at Read the Docs)
* `Repository <https://github.com/tkf/python-epc>`_ (at GitHub)
* `Issue tracker <https://github.com/tkf/python-epc/issues>`_ (at GitHub)
* `PyPI <http://pypi.python.org/pypi/epc>`_
* `Travis CI <https://travis-ci.org/#!/tkf/python-epc>`_ |build-status|

Other resources:

* `kiwanami/emacs-epc <https://github.com/kiwanami/emacs-epc>`_
  (Client and server implementation in Emacs Lisp and Perl.)
* `tkf/emacs-jedi <https://github.com/tkf/emacs-jedi>`_
  (Python completion for Emacs using EPC server.)

.. |build-status|
   image:: https://secure.travis-ci.org/tkf/python-epc.png
           ?branch=master
   :target: http://travis-ci.org/tkf/python-epc
   :alt: Build Status


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
This is a stripped version of `examples/echo/client.el`_ included in
python-epc repository_.::

   (require 'epc)

   (defvar my-epc (epc:start-epc "python" '("my-server.py")))

   (deferred:$
     (epc:call-deferred my-epc 'echo '(10))
     (deferred:nextc it
       (lambda (x) (message "Return : %S" x))))

   (message "Return : %S" (epc:call-sync my-epc 'echo '(10 40)))


.. _examples/echo/client.el:
   https://github.com/tkf/python-epc/blob/master/examples/echo/client.el

If you have carton_ installed, you can run the above sample by
simply typing the following commands::

   make elpa        # install EPC in a separated environment
   make run-sample  # run examples/echo/client.el

.. _carton: https://github.com/rejeep/carton


For example of bidirectional communication and integration with GTK,
see `examples/gtk/server.py`_.

.. _examples/gtk/server.py:
   https://github.com/tkf/python-epc/blob/master/examples/gtk/server.py

EPC (RPC stack for Emacs Lisp) for Python
=========================================

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


What is this?
-------------

EPC is an RPC stack for Emacs Lisp and Python-EPC is its server side
and client side implementation in Python.  Using Python-EPC, you can
easily call Emacs Lisp functions from Python and Python functions from
Emacs.  For example, you can use Python GUI module to build widgets
for Emacs (see `examples/gtk/server.py`_ for example).

Python-EPC is tested against Python 3.7, 3.8 and 3.10.
Previous versions worked with Python 2.6, 2.7, 3.2 and 3.3.

Install
-------

To install Python-EPC and its dependency sexpdata_, run the following
command.::

   pip install epc

.. _sexpdata: https://github.com/tkf/sexpdata


Usage
-----

Save the following code as ``my-server.py``.
(You can find functionally the same code in `examples/echo/server.py`_)::

   from epc.server import EPCServer

   server = EPCServer(('localhost', 0))

   @server.register_function
   def echo(*a):
       return a

   server.print_port()
   server.serve_forever()


And then run the following code from Emacs.
This is a stripped version of `examples/echo/client.el`_ included in
Python-EPC repository_.::

   (require 'epc)

   (defvar my-epc (epc:start-epc "python" '("my-server.py")))

   (deferred:$
     (epc:call-deferred my-epc 'echo '(10))
     (deferred:nextc it
       (lambda (x) (message "Return : %S" x))))

   (message "Return : %S" (epc:call-sync my-epc 'echo '(10 40)))


.. _examples/echo/server.py:
   https://github.com/tkf/python-epc/blob/master/examples/echo/server.py
.. _examples/echo/client.el:
   https://github.com/tkf/python-epc/blob/master/examples/echo/client.el

If you have carton_ installed, you can run the above sample by
simply typing the following commands::

   make elpa        # install EPC in a separated environment
   make run-sample  # run examples/echo/client.el

.. _carton: https://github.com/rejeep/carton


For example of bidirectional communication and integration with GTK,
see `examples/gtk/server.py`_.  You can run this example by::

   make elpa
   make run-gtk-sample  # run examples/gtk/client.el

.. _examples/gtk/server.py:
   https://github.com/tkf/python-epc/blob/master/examples/gtk/server.py


License
-------

Python-EPC is licensed under GPL v3.
See COPYING for details.

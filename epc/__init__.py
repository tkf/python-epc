# [[[cog import cog; cog.outl('"""\n%s\n"""' % file('../README.rst').read())]]]
"""
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

Python-EPC is tested against Python 2.6, 2.7 and 3.2.

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

"""
# [[[end]]]

# Copyright (c) 2012 Takafumi Arakaki
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.

# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__version__ = '0.0.3.dev3'
__author__ = 'Takafumi Arakaki'
__license__ = 'BSD License'

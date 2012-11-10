# [[[cog import cog; cog.outl('"""\n%s\n"""' % file('../README.rst').read())]]]
"""
EPC (RPC stack for Emacs Lisp) server for Python
================================================

Links:

* `Documentaions (at Read the Docs) <http://python-epc.readthedocs.org/>`_
* `Repository (at GitHub) <https://github.com/tkf/python-epc>`_
* `Issue tracker (at GitHub) <https://github.com/tkf/python-epc/issues>`_
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

   make elpa        # install EPC in a separated environment
   make run-sample  # run client.el

.. _carton: https://github.com/rejeep/carton

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

__version__ = '0.0.1.dev3'
__author__ = 'Takafumi Arakaki'
__license__ = 'BSD License'

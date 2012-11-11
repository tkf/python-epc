#!/usr/bin/env python

"""
An example of using GTK from Emacs.

* Manipulate GTK window from Emacs:

  - `destroy` (`pyepc-sample-gtk-destroy`):
     Close GTK window from Emacs command

  - `set_button_label` (`pyepc-sample-gtk-set-button-label`):
     Change GUI button label from Emacs command.

* (Not yet implemented) Manipulate Emacs from GTK GUI.

"""

import threading
import logging

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from epc.server import ThreadingEPCServer, setuplogfile


class SampleGTKServer(object):

    def __init__(self):
        self.setup_gtk()
        self.setup_epc()

    def setup_gtk(self):
        gtk.threads_init()

        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        # Quit when window is closed
        self.window.connect("destroy", self.destroy)

        # Creates a new button with the label "Hello World".
        self.button = gtk.Button("Push me!")
        self.button.connect("clicked", self.clicked, None)

        # Show widgets and window
        self.window.add(self.button)
        self.button.show()
        self.window.show()

    def setup_epc(self):
        self.server = ThreadingEPCServer(('localhost', 0))

        # Setup logger
        self.server.logger.setLevel(logging.DEBUG)
        setuplogfile()

        # Setup server thread
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.allow_reuse_address = True

        # Define and register RPC functions
        def destroy():
            gobject.idle_add(gtk.Widget.destroy, self.window)

        def set_button_label(label):
            gobject.idle_add(self.button.set_label, label)

        self.server.register_function(destroy)
        self.server.register_function(set_button_label)

    def clicked(self, widget, data=None):
        # TODO: call client function here
        pass

    def destroy(self, widget, data=None):
        self.server.shutdown()
        gtk.main_quit()

    def main(self):
        self.server_thread.start()
        self.server.print_port()
        gtk.main()


if __name__ == "__main__":
    server = SampleGTKServer()
    server.main()

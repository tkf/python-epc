(require 'cl)
(require 'epcs)

(defvar pyepc-epcs
  (epcs:server-start
   (lambda (mngr)
     (lexical-let ((mngr mngr))
       (epc:define-method mngr 'echo 'identity)
       (epc:define-method
        mngr 'ping-pong
        (lambda (&rest args) (epc:call-sync mngr 'pong args)))))
   9999))

(when noninteractive
  (sleep-for 60))

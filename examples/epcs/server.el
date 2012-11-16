(require 'cl)
(require 'epcs)

(defvar pyepc-epcs
  (epcs:server-start
   (lambda (mngr)
     (lexical-let ((mngr mngr))
       (epc:define-method mngr 'echo 'identity)
       (epc:define-method
        mngr 'ping-pong
        (lambda (&rest args)
          (message "EPCS> PING-PONG got: %S" args)
          (deferred:$
            (epc:call-deferred mngr 'pong args)
            (deferred:nextc it
              (lambda (&rest args)
                (message "EPCS> PONG returns: %S" args)
                args)))))))
   9999))

(when noninteractive
  ;; Start "event loop".
  (loop repeat 600
        do (sleep-for 0.1)))

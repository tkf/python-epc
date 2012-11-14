(require 'cl)
(require 'epcs)

(defvar pyepc-epcs
  (epcs:server-start
   (lambda (mngr)
     (epc:define-method mngr 'echo 'identity))
   9999))

(when noninteractive
  (sleep-for 60))

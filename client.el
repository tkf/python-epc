(require 'epc)

(setq epc (epc:start-epc "python" '("-m" "epc.server")))

(deferred:$
  (epc:call-deferred epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))


(message "Return : %S" (epc:call-sync epc 'echo '(10 40)))

(deferred:$
  (epc:call-deferred epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))
(deferred:$
  (epc:call-deferred epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))
(deferred:$
  (epc:call-deferred epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))
(deferred:$
  (epc:call-deferred epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))
(deferred:$
  (epc:call-deferred epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))
(deferred:$
  (epc:call-deferred epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))
(deferred:$
  (epc:call-deferred epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))
(deferred:$
  (epc:call-deferred epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))
(deferred:$
  (epc:call-deferred epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))
(deferred:$
  (epc:call-deferred epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))
(deferred:$
  (epc:call-deferred epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))
(deferred:$
  (epc:call-deferred epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))
(deferred:$
  (epc:call-deferred epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))
(deferred:$
  (epc:call-deferred epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))
(deferred:$
  (epc:call-deferred epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))
(deferred:$
  (epc:call-deferred epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))


(message "Return : %S" (epc:call-sync epc 'echo '(10 40)))

(epc:stop-epc epc)

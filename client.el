(require 'epc)
(when noninteractive
  (load "subr")
  (load "byte-run"))
(eval-when-compile (require 'cl))

(defvar my-epc (epc:start-epc "python" '("-m" "epc.server")))
(set-process-query-on-exit-flag
 (epc:manager-server-process my-epc) nil)

(deferred:$
  (epc:call-deferred my-epc 'echo 10)
  (deferred:nextc it
    (lambda (x) (message "Return : %S" x))))


(message "Return : %S" (epc:call-sync my-epc 'echo '(10 40)))

(loop for i from 1 to 5
      do (deferred:$
           (epc:call-deferred my-epc 'echo i)
           (deferred:nextc it
             (lambda (x) (message "Return : %S" x)))))

(message "Return : %S"
         (epc:sync my-epc (epc:query-methods-deferred my-epc)))

(epc:stop-epc my-epc)

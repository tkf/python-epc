(require 'epc)
(when noninteractive
  (load "subr")
  (load "byte-run"))
(eval-when-compile (require 'cl))

(message "Start EPC")

(defvar my-epc (epc:start-epc
                (or (getenv "PYTHON") "python")
                '("-m" "epc.server" "--log-traceback"
                  "--allow-dotted-names" "os")))

(message "Start request")

(message "listdir(\".\") returns: %S"
         (epc:call-sync my-epc 'listdir '(".")))

(message "path.join(\"a\", \"b\", \"c\") returns: %S"
         (epc:call-sync my-epc 'path.join '("a" "b" "c")))

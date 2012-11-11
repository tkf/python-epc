(require 'epc)
(when noninteractive
  (load "subr")
  (load "byte-run"))
(eval-when-compile (require 'cl))

(message "Start EPC")

(defvar pyepc-sample-gtk-dir
  (if load-file-name
      (file-name-directory load-file-name)
    default-directory))

(defvar pyepc-sample-gtk-epc
  (epc:start-epc (or (getenv "PYTHON") "python")
                 (list (expand-file-name "server.py" pyepc-sample-gtk-dir))))

(defun pyepc-sample-gtk-destroy ()
  (interactive)
  (epc:call-deferred pyepc-sample-gtk-epc 'destroy nil))

(defun pyepc-sample-gtk-set-button-label (label)
  (interactive "sButton label: ")
  (epc:call-deferred pyepc-sample-gtk-epc 'set_button_label (list label)))

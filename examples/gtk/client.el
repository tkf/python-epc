(require 'epc)
(when noninteractive
  (load "subr")
  (load "byte-run"))
(eval-when-compile (require 'cl))

(message "Start EPC")

(defvar pyepc-sample-gtk-dir
  (if load-file-name
      (file-name-directory load-file-name)
    default-directory)
  "Path to examples/gtk/.")

(defvar pyepc-sample-gtk-epc
  (epc:start-epc (or (getenv "PYTHON") "python")
                 (list (expand-file-name "server.py" pyepc-sample-gtk-dir)))
  "EPC manager object for GTK server example.")

(epc:define-method pyepc-sample-gtk-epc
                   'message
                   (lambda (&rest args) (message "%S" args)))

(defun pyepc-sample-gtk-destroy ()
  "Close GTK window"
  (interactive)
  (deferred:nextc
    (epc:call-deferred pyepc-sample-gtk-epc 'destroy nil)
    (lambda ()
      (epc:stop-epc pyepc-sample-gtk-epc)
      (message "EPC server is stopped."))))

(defun pyepc-sample-gtk-set-button-label (label)
  "Change GUI button label."
  (interactive "sButton label: ")
  (epc:call-deferred pyepc-sample-gtk-epc 'set_button_label (list label)))

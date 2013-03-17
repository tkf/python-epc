#!/bin/sh

CARTON=${CARTON:-carton}
EMACS=${EMACS:-emacs}
PYTHON=${PYTHON:-python}

cd $(dirname $0)/../..
${CARTON} exec ${EMACS} -batch -Q -l examples/epcs/server.el &
epid=$!
trap 'kill -TERM '$epid EXIT
echo "Emacs is running at $epid"

sleep 0.1
${PYTHON} examples/epcs/client.py "$@"

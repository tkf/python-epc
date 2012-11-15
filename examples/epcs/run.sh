#!/bin/sh

cd $(dirname $0)/../..
carton exec emacs -batch -Q -l examples/epcs/server.el &
epid=$!
trap 'kill -TERM '$epid EXIT
echo "Emacs is running at $epid"

sleep 0.1
python examples/epcs/client.py

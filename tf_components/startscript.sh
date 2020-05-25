#!/bin/bash
pkill -9 python3
source tfenv/bin/activate
python3 wsgi.py &
disown

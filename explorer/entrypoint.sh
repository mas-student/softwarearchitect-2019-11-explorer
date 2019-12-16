#!/bin/bash

if [ "x$1" = "xtest" ]; then
    py.test .
else
    python /home/user/explorer/main.py
fi
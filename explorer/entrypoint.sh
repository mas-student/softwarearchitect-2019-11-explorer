#!/bin/bash

if [ "x$1" = "xtest" ]; then
    py.test .
elif [ "x$1" = "xdev" ]; then
    adev runserver /home/user/explorer/main.py
else
    python /home/user/explorer/main.py
fi
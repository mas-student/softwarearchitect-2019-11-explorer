#!/bin/bash

if [ "x$1" = "xtest" ]; then
    py.test .
elif [ "x$1" = "xdev" ]; then
    adev runserver -p 8080 /home/user/loader/main.py
else
    if [ "x$DEV" != "x" ]; then
      adev runserver -p 8080 /home/user/loader/main.py
    else
      python /home/user/loader/main.py
    fi
fi
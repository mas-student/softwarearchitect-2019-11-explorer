#!/bin/bash

if [ "x$1" = "xtest" ]; then
    py.test .
elif [ "x$1" = "xdev" ]; then
    adev runserver -p 8080 /home/user/backend/main.py
else
    if [ "x$DEV" != "x" ]; then
      adev runserver -p 8080 /home/user/backend/main.py
    else
      python /home/user/backend/main.py
    fi
fi
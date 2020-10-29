#!/bin/sh
exec /usr/local/bin/gunicorn wsgi:app -c gunicorn.conf.py
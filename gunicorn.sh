#!/bin/bash
. $(dirname $0)/.env.sh

gunicorn SocialPlus.wsgi:application

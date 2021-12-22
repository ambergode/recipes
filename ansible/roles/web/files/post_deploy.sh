#!/bin/bash

. env.sh

python manage.py migrate
if [ $? -ne 0 ]; then
  echo "Failed to migrate" >&2
  exit 1
fi

exit 0


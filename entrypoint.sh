#!/bin/bash

set -eo pipefail

python manage.py migrate
python manage.py collectstatic --no-input

exec "$@"

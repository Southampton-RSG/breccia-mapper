#!/bin/bash

set -eo pipefail

python manage.py migrate
echo "[{\"model\": \"sites.site\",\"pk\": 1,\"fields\": { \"domain\": \"${SITE_URL}\", \"name\": \"${PROJECT_SHORT_NAME}\" }}]" | python manage.py loaddata --format=json -
python manage.py selectiveloaddata breccia_mapper/fixtures/bootstrap_customizer_theme.json
python manage.py loaddata --format=json bootstrap_customizer_sitetheme
python manage.py collectstatic --no-input

exec "$@"

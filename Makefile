.PHONY: docs
docs:
	cd docs; make clean; make html; cd ..
	yes 'yes' | env/bin/python manage.py collectstatic

.PHONY: lint
lint:
	prospector

.PHONY: staging
staging:
	ansible-playbook -v -i staging.yml playbook.yml -u jag1e17 -K

.PHONY: production
production:
	ansible-playbook -v -i production.yml playbook.yml -u jag1e17 -K

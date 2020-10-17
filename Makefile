default: install migrate collectstatic
	venv/bin/python manage.py runserver

venv:
	python -m venv venv

install: venv
	venv/bin/pip install -r requirements.txt

migrate: install
	venv/bin/python manage.py makemigrations
	venv/bin/python manage.py migrate

shell: install
	venv/bin/python manage.py shell

test: install
	venv/bin/python manage.py test

collectstatic: install
	mkdir static
	venv/bin/python manage.py collectstatic

clean:
	rm -rf venv static db.sqlite3

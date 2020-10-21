PORT=8000
default: install migrate collectstatic run

make run:
	venv/bin/python manage.py runserver ${PORT}

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
	mkdir -p staticfiles
	mkdir -p static
	venv/bin/python manage.py collectstatic --no-input

clean:
	rm -rf venv static staticfiles db.sqlite3

format fmt: install
	venv/bin/black .

freeze:
	venv/bin/pip freeze > requirements.txt

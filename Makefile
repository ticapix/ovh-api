PY_ENV=./venv3

export PATH := $(PY_ENV)/bin:$(PATH)

$(PY_ENV):
	python3 -m venv $(PY_ENV)
	pip install --upgrade pip
	pip install -r requirements.txt

install: $(PY_ENV)

run: install
	python run.py

test: install
	ASYNC_TEST_TIMEOUT=20 python -m tornado.testing tests

PY_ENV=./venv3
# NPM_BIN=$(shell npm bin)


help: # usage
	@cat Makefile | grep -e "\w\+:.*" #| sed 's/(.*):.*#(.*)/\1: \2/g'

# $(NPM_BIN):
# 	npm install

$(PY_ENV):
	python3 -m venv $(PY_ENV)
	$(PY_ENV)/bin/pip install --upgrade pip
	$(PY_ENV)/bin/pip install -r requirements.txt

install: $(PY_ENV) # $(NPM_BIN)  install deps

run: install
	$(PY_ENV)/bin/python run.py

test: install
	ASYNC_TEST_TIMEOUT=20 $(PY_ENV)/bin/python tests.py

# convert: install # validate yaml
# 	$(PY_ENV)/bin/python ./convert.py

# validate:
# 	`npm bin`/swagger-cli validate apis-*.yml
# 	# `npm bin`/swagger-cli validate apis-ip.yml
# 	# cat apis-me.yml | yq '.paths'

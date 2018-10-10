PY_ENV=./venv3
# NPM_BIN=$(shell npm bin)


help: # usage
	@cat Makefile | grep -e "\w\+:.*" #| sed 's/(.*):.*#(.*)/\1: \2/g'

# $(NPM_BIN):
# 	npm install

export PATH := $(PY_ENV)/bin:$(PATH)

$(PY_ENV):
	python3 -m venv $(PY_ENV)
	pip install --upgrade pip
	pip install -r requirements.txt

install: $(PY_ENV) # $(NPM_BIN)  install deps

run: install
	python run.py

test: install
	which python
	ASYNC_TEST_TIMEOUT=20 python tests.py

# convert: install # validate yaml
# 	$(PY_ENV)/bin/python ./convert.py

# validate:
# 	`npm bin`/swagger-cli validate apis-*.yml
# 	# `npm bin`/swagger-cli validate apis-ip.yml
# 	# cat apis-me.yml | yq '.paths'

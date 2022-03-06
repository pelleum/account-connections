SHELL := /bin/bash

docker_image = account-connections
docker_username = pelleum
formatted_code := app/ migrations/ tests/ tasks.py


.ONESHELL:

rev_id = ""
migration_message = ""

.PHONY: test run

requirements.txt: requirements.in
	pip-compile --quiet --generate-hashes --output-file=$@

format:
	isort $(formatted_code)
	black $(formatted_code)

lint:
	pylint app

run:
	python -m app --reload

check:
	black --check $(formatted_code)

build:
	docker build -t $(docker_username)/$(docker_image):latest .

# Stop and tear down any containers after tests run
test: build
	function removeContainers {
		docker-compose -p account-connections-continuous-integration rm -s -f test_db
	}
	trap removeContainers EXIT
	docker-compose -p account-connections-continuous-integration run --rm continuous-integration;

push:
	docker push $(docker_username)/$(docker_image):latest

# TODO: This should have variables to pass to it.
migration:
	if [ -z $(rev_id)] || [ -z $(migration_message)]; \
	then \
		echo -e "\n\nmake migration requires both a rev_id and a migration_message.\nExample usage: make migration rev_id=0001 migration_message=\"my message\"\n\n"; \
	else \
		alembic revision --autogenerate --rev-id "$(rev_id)" -m "$(migration_message)"; \
	fi

migrate:
	alembic upgrade head

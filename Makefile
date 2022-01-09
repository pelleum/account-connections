SHELL := /bin/bash

docker_image = pelleum_api
docker_username = adamcuculich
formatted_code := app/ migrations/


.ONESHELL:

rev_id = ""
migration_message = ""

requirements.txt:
	pip-compile --generate-hashes --output-file=requirements.txt requirements.in

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
	docker build -t $(docker_image):latest .

test:
	docker run $(docker_image):latest \
		black --check $(formatted_code)

push:
	# check to make sure this is correct ...
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

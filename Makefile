SHELL := /bin/bash

docker_image = pelleum_api
docker_username = adamcuculich
formatted_code := app/ migrations/


.ONESHELL:

requirements.txt:
	pip-compile --generate-hashes --output-file=requirements.txt requirements.in

black:
	black $(formatted_code)

lint:
	pylint app

run-dev:
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
generate-migrations:
	alembic revision --autogenerate --rev-id "0001" -m "users theses and posts"

migrate:
	alembic upgrade head

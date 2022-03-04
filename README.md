# Account Connections API
This repository contains code relevant to linking external brokerage accounts to Pelleum.

## High-level Overview
### API Endpoints
This service contains [private API endpoints](https://github.com/pelleum/account-connections/blob/master/app/infrastructure/web/endpoints/private/institutions.py), which the service, [pelleum-api](https://github.com/pelleum/pelleum-api), utilizes to manage users' brokerage account connections.

### Periodic, Asynchronous Tasks
This service also contains 2 periodic, asynchronous tasks. They are as follows:
1. [JWT Refresh Task](https://github.com/pelleum/account-connections/blob/master/app/infrastructure/tasks/refresh_tokens.py): refreshes each user's brokerage JSON web token every 24 hours. This allows for the user to not have to repeatedly relink his or her brokerage after the initial JSON web token expires.
2. [User Holdings Update Task](https://github.com/pelleum/account-connections/blob/master/app/infrastructure/tasks/get_holdings.py): Syncs Pelleum-tracked brokerage holdings with the user's brokerage (source of truth) every 24 hours.


**NOTE:** At present, [User Holdings Update Task](https://github.com/pelleum/account-connections/blob/master/app/infrastructure/tasks/get_holdings.py) starts 12 hours after the [JWT Refresh Task](https://github.com/pelleum/account-connections/blob/master/app/infrastructure/tasks/refresh_tokens.py) starts to leave maximum time for both of their completions.

## Local Development Instructions

## Setup virtual environment
- Run `python3 -m pip install --user --upgrade pip`
- Run `python3 -m pip install --user virtualenv`
- Run `python3 -m venv env`
- Activate virtual environment with `source env/bin/activate`
- Install packages with `python3 -m pip install -r requirements.txt`

## Run API
- Install Docker
- Set environment variables in `.env` file in the project's root directory (get from senior engineer)
- Run `docker-compose up -d db` (this will spin up a local postgreSQL database)
- Run `make run` (this runs the server locally)
- Can stop docker container by running `docker stop <CONTAINER ID>`, CONTAINER_ID can be found by running `docker ps`

## Test API Calls
- Can use Postman to test calls (Can get Postman collection from senior engineer)
- Can also test calls via [API Docs](http://0.0.0.0:8000/docs)

## Push Docker Image to Docker Hub
- Run `docker login`, get credentials from bitwarden
- Run `docker build -t pelleum/account-connections .` to build docker container
- Run `docker push pelleum/account-connections` to push to Docker Hub
- Verify docker image has been pushed to Docker Hub

## Deploy Cluster in AWS
- Update account-connections service in AWS console
- Make sure to use latest version and check Force new deployment box
- Verify by viewing logs in CloudWatch

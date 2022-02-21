# Account Connections API
This repository contains code relevant to linking external brokerage accounts to Pelleum.

## Local Development Instructions

## Setup virtual environment
- Run `python3 -m pip install --user --upgrade pip`
- Run `python3 -m pip install --user virtualenv`
- Run `python3 -m venv .venv`
- Activate virtual environment with `source .venv/bin/activate`
- Install packages with `python3 -m pip install -r requirements.txt`
- If `pg_config executable not found` error is encountered, try installing postgresql via `brew install postgresql`

## Run account-connections
- Install pgAdmin
- Set environment variables in .env file (get from senior engineer)
- Run `make run`
- Setup database schemas via pgAdmin

## Test API calls
- Can use Postman to test calls (Can get Postman collection from senior engineer)
- Can also test calls via [API Docs](http://0.0.0.0:1201/docs)

## Deploy docker container
- Run `docker login`, get credentials from bitwarden
- Run `docker build -t pelleum/account-connections .` to build docker container
- Run `docker push pelleum/account-connections` to push to docker hub
- Verify container is deployed in docker hub

## Deploy cluster in AWS
- Update account-connections service in AWS console
- Make sure to use latest version and check Force new deployment box
- Verify by viewing logs in CloudWatch
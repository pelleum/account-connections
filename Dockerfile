FROM python:3.8

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

# Database Environment Variables
ENV DB_URL=postgres://postgres:postgres@localhost:5432/pelleum-dev
ENV SCHEMA=Something

# Encryption Key
ENV ENCRYPTION_SECRET_KEY=nope

# Robinhood Environment Variables
ENV ROBINHOOD_CLIENT_ID=thisismyrobinhoodclientid
ENV ROBINHOOD_DEVICE_TOKEN=this-is-my-device-token

# Auth Environment Variables
ENV JSON_WEB_TOKEN_SECRET=nicetry
ENV TOKEN_URL=/public/auth/users/login
ENV JSON_WEB_TOKEN_ALGORITHM=Something

# Server Environment Variables
ENV SERVER_PORT=1201
ENV OPENAPI_URL="/openapi.json"

EXPOSE $SERVER_PORT

CMD ["python", "-m", "app"]
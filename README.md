# Securing with Keycloak IPD Demo

This is demo, how to secure FastAPI python application with Keycloak for browser and non-browser flows:

* `authorization_code` flow for web-application
* `authorization_code` flow for CLI tool
* `device_code` flow for CLI tool

This repository contains:
* docker compose specification
* python application in `/app` folder

## Requirements

* Installed `miniconda` (you can download from https://docs.conda.io/en/latest/miniconda.html)
* Installed docker and docker-compose 

## Setup

1. Run `docker-compose up -d` to run keycloak services
2. Run `./add-users.sh` to create users `user` and `user-admin` with `password` as a password, additionally `user-admin` has `super-admin` role
3. Create and activate conda environment:\
   `cd app && conda create -p .env -f environment.yml && conda activate ./.env`

## Demo

From the previous step you are in `app/` folder and with activated conda environment:

Run `python app.py` - this will run FastAPI on port 5000 (if you see port conflict errors - please check, that no other services are running there. Hello MacOS :)

Now it's possible to do several options:

### authorization_code browser flow

1. Navigate to `http://localhost:5000/auth` and client on the link - you will be redirected to Keycloak. After entering credentials, you will be redirected to `http://localhost:5000/callback` where you should see JSON response with access, refresh and id_token. 

2. You can now use access token to access protected resouce. For this in console run `export JWT=<TOKEN>` and make `curl -H"Authorization: Bearer $JWT" http://localhost:5000` and `curl -H"Authorization: Bearer $JWT" http://localhost:5000/admin`. For second call you need a token from `user-admin`.

Alternatively you can use swagger to navigate to resources - use http://localhost:5000/docs, click "Authorize" and in "authorization_code" flow section use `app1` as a client_id and `CLIENTSECRET` as a client_secret. After successfull authorization you will be able to call `/` and `/admin` from swagger

### device_code flow

1. Open another terminal, active conda environment with `conda activate ./.env`
2. Run `python app/cli_device_flow.py`. The token will be obtained with *device_code* flow and you will be able to see results of calling service API endpoints:

```
...
RECEIVED TOKEN:
<TOKEN IS HERE>

Logged in as user-id=f7e74602-19b8-41ba-9f6c-f33d9247be17

Requesting default endpoint:
{'account': {'user': {'user_id': 'f7e74602-19b8-41ba-9f6c-f33d9247be17', 'username': 'user', 'is_superadmin': False}}}
Requesting admin endpoint:
{'detail': 'Access denied - super-admin rights are needed'}
```

### Keycloak user session logout

Navigate to http://localhost:8080/realms/app/account/#/ and click "Sign out" in the right top corner.

## Cleanup
1. `docker-compose down --volumes` to stop services and clean-up volumes

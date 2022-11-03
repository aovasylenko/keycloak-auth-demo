Securing with Keycloak IPD Demo
===============================

This is demo, how to secure FastAPI python application with Keycloak for browser and non-browser flows:

* `authorization_code` flow for web-application
* `authroization_code` flow for CLI tool
* `device_code` flow for CLI tool

This repository contains:
* docker compose specification
* python application in `/app` folder

Requirements
------------
* Installed `miniconda` (you can download from https://docs.conda.io/en/latest/miniconda.html)
* Installed docker and docker-compose 

Setup
-----
1. Run `docker-compose up -d` to run keycloak services
2. Run `./add-users.sh` to create users `user` and `user-admin` with `password` as a password, additionally `user-admin` has `super-admin` role
3. Create and activate conda environment:\
   `cd app && conda create -p .env -f environment.yml && conda activate ./.env`

Cleanup
-------
1. `docker-compose down --volumes` to stop services and clean-up volumes

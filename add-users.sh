#!/bin/bash

set -ex

docker-compose exec keycloak /opt/keycloak/bin/kcadm.sh config credentials --server "http://localhost:8080/" --realm master --user admin --password admin

docker-compose exec keycloak /opt/keycloak/bin/kcadm.sh create users -r app -s username=user -s enabled=true
docker-compose exec keycloak /opt/keycloak/bin/kcadm.sh set-password -r app --username user --new-password password

docker-compose exec keycloak /opt/keycloak/bin/kcadm.sh create users -r app -s username=user-admin -s enabled=true
docker-compose exec keycloak /opt/keycloak/bin/kcadm.sh set-password -r app --username user-admin --new-password password
docker-compose exec keycloak /opt/keycloak/bin/kcadm.sh add-roles -r app --uusername user-admin --rolename super-admin

echo "Done"
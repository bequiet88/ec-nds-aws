# ec-nds-aws

Pretix Update

```
ssh ubuntu@tickets.ec-niedersachsen.de #valid ssh key required

sudo su - pretix

cd pretix

git status

git diff # check for  changes in Dockerfile and plugins.txt

git stash # preserve changes in Dockerfile and plugins.txt

git fetch origin

git checkout v<latest version>

git stash apply

git mergetool #if stash apply fails

cd ..

docker-compose stop # build only works with stopped pretix

docker-compose build

docker tag pretix_web:latest pretix_web:v<latest version> # tag the latest version to keep versoin record on local docker registry 

### reboot here if needed

docker ps -a # find stopped redis and postgres container

docker start 419d47d5153a

docker start 1d75da693007

docker-compose up -d web

docker inspect pretix_web_1 | grep Image # check if latest version image used

docker images | grep pretix # id of latest must match running image


```

You are done.


Testing secret injection

# Overview

* The web application is now a stand-alone Flask app, with the Dash app embedded inside it. (Flask App(Dash App))
* 4 containers are used (webapp, certbot, nginx, datadog_agent)

# Start up
1. Manual startup will use TLS certificates contained in /infrastructure/certbot
2. Generate certs can be done by running startup-generate-certs.sh

# TLS Update

When TLS certs expire, it's a cunt. Need to bring system down in Docker. Reinitialise with `start-up-generate-certs.sh`. Shell into the NGINX container to copy the new certs to local machine. Add them to github secrets. Then rebuild whole pipeline.

**Lazy Option**
1. Bring app down with `sudo docker stop $(sudo docker ps -a -q)`
2. Generate new certs with `. startup-generate-certs.sh` (these only exist in the nginx running container)

**Complete Option**

Copy the newly created certs into github secrets so can rebuild the full pipeline with working TLS

3. Obtain the container ID for Nginx with `docker ps`
4. Copy both keys to $HOME as files 

`docker cp -L e9e73443e9f2:/etc/letsencrypt/live/worldatlas.org/privkey.pem ~/privkey.pem`

`docker cp -L e9e73443e9f2:/etc/letsencrypt/live/worldatlas.org/fullchain.pem ~/fullchain.pem`

Noting the e9e73443e9f2 above is the containerID of the nginx container

5. Copy the content of each key file into GITHUB SECRETS (repo > settings > secrets > actions > ...)
6. (OPTIONAL) Rebuild whole deployment by manually rerunning the github actions for `deploy` (takes 15 mins and can be a bitch)




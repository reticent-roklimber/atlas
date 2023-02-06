# Quick Start

### Run from a local machine (without Docker)



### Run from a local machine (with Docker)

System requirements: ~4GB RAM


# Contents

## What is this site?

It's an ad-free educational website that allows you to visualise thousands of public datasets about the world. Inspired by Microsoft Encarta 1995, it's mission is to make important data more accessible, for everyone. The idea was something like a modernised replacement for the paper World Atlas, as Wikipedia replaced the paper encyclopaedia.

## What this site is not

Perfect. There have been many tradeoffs made to experiment with some of these ideas, and I've developed it on my own so far.

## Why I built it

The internet is a fucking mess. Important data is scattered around the place. Most people don't have any idea where to find good data, nor how to visualise or interpret it. I've tried to find some of it (good data) and visualise it so I could learn things. Then I thought others might find it useful to learn also. I also wanted to experiment with modern tools in data science, like Plotly Dash.

See my [article](https://medium.com/towards-data-science/ive-built-a-public-world-atlas-with-2-500-datasets-to-explore-8b9ae799e345) on Towards Data Science for a full white paper pitch, with jokes.

## How it works (generally)

## How it works (nerd level detail)

## How to collaborate

This is my first proper open source project. I'd love some help. There are small things to be tweaked and more deep level things that will require low level detail and access at a collaborator level. Feel free to chuck PR's my way or incident tickets.

## Development Roadmap (stuff I want to fix)

1. ### The front end experience

**Expanding the mapping capabilities beyond Plotly charts**

Presently the site is built as a Flask app, wrapping a Plotly Dash (Python) web app. Most of the visualisations such as charts and maps are out-of-the box Plotly javascript charts. Some I've pushed hard but, at base, I think the main map is limited as it is really just a Choropleth chart. I'd love to explore more open frameworks for map specific stuff, like Leaflet and Mapbox.

2. ### 




# Clean up


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




# Quick Start

System requirements: ~4GB memory (RAM) on your local machine.

## Run from a local machine *without* Docker 

This is the least complex way to run the app as we will spin it up directly from your local webserver on your Python kernal. However it is also fidly on some operating systems like Windows (especially if you are running Annaconda). If you're on Linux or MacOs, you should be fine.

### 1. Clone repository to your machine 

Recommend using [Github Desktop](https://desktop.github.com/) or Git command line interface (CLI) in a terminal

`git clone git@github.com:danny-baker/atlas.git`

### 2. Setup virtual environment 

This varies slightly between Linux, MacOS, Windows. 

`python3 -m venv venv`

`source venv/bin/activate`

### 3. Ensure you are in the project root folder

`cd atlas` (or similar)

### 4. Install python packages

`pip3 install -r requirements.txt`

Note you may struggle if trying to install with Annaconda with 'conda install'. This is because the site is built and tested in linux with the 'pip3' python package installer. If you get stuck here and can't use pip3 for some reason, I recommend using the Docker approach in the next section. This means the app will be built in a linux container and will run perfectly every time.

### 5. Spin up the app in your local web browser!

`python3 wsgi.py`

This is the app entry point. The above command should start everything happening. Give it 30 seconds to spin up, and the console should spit out a URL you can put and paste into the browser. Copy-paste this and hopefully you can play with the site locally. 

## Run from a local machine *with* Docker (reliable)

This is the most reliable method to run the app as a stand-alone container on your local machine. In fact, this is how the app is deployed on the production environment, along with a few other special containers to help keep everything working. You will need to have Docker installed. If you are unfamiliar with Docker, now is the time to learn. I've provided step by step guide to containerise the app in Docker and view it from your web browser. The cool thing about this: no faffing about with virtual python environments and installing requirements.txt. All that shit is abstracted away and happens when the Docker image is created (which contains the app on a virtualised linux operating system)

### 1. Install Docker to your local machine

Follow the relevant pathway for your operating system, on their website [here](https://docs.docker.com/get-docker/).

### 2. Clone repository to your machine 

Recommend using [Github Desktop](https://desktop.github.com/) or Git command line interface (CLI) in a terminal

`git clone git@github.com:danny-baker/atlas.git`

### 3. Build the app into a Docker image and run it as a container

From a terminal in the main repo root directory

`docker build . --tag atlas_app`

This will build the main Python web application into a Docker image, based on the `Dockerfile` in the repo. It will take a good 3-5 minutes to complete but you should see a bunch of outputs in the terimal window. During this build, an Ubuntu linux operating system is utilised, and all the python modules and dependencies will be installed. The main image file is around 3GB when finished. The reason it's so large is that all of my data files are currently being containerised also, so the app has direct access to them at run-time. Totally aware there are better ways to do this, such as moving all the processed data files to S3 bucket blob storage etc.

**ENCOUNTERED PROBLEM ON MAC DOCKER. IT WONT BUILD**

### 4. View running container from your web browser

You should just be able to open a web browser and punch in whatever the IP and port is displayed in the terminal output from Docker.

This doesn't always work, but the running app container should be able to bind to TCP/IP port 80 on your machine, so that you can access it from your web browser. Sometimes I've found this can be buggy on Docker desktop on Windows and Mac. 

# Slow Start

## What is this site?

It's an educational website (prototype) that allows you to visualise thousands of public datasets about the world. Inspired by Microsoft Encarta 1995, it's mission is to make important data more accessible, for everyone. The idea was something like a modernised replacement for the paper World Atlas, as Wikipedia replaced the paper encyclopaedia.

## What this site is not

Perfect. There have been *many* tradeoffs made to experiment with some of these ideas, and I've developed it on my own so far.

## Why I built it

The internet is en ever expanding fucking mess. Important data is scattered around the place. Most people don't have any idea where to find good data, nor how to visualise or interpret it. I've tried to find some of it (good data) and visualise it so I could learn things. Then I thought others might find it useful to learn also. I also wanted to experiment with modern tools in data science, like Plotly Dash.

See my [article](https://medium.com/towards-data-science/ive-built-a-public-world-atlas-with-2-500-datasets-to-explore-8b9ae799e345) on Towards Data Science for a full white paper pitch, with jokes.

## How it works (generally)

## How it works (nerd level detail)

## How to collaborate

This is my first proper open source project. I'd love some help. There are small things to be tweaked and more deep level things that will require low level detail and access at a collaborator level. Feel free to chuck PR's my way or incident tickets.

## Development Roadmap (stuff I want to fix)

1. ### The front end experience

**Expanding the mapping capabilities beyond Plotly charts**

Presently the site is built as a Flask app, wrapping a Plotly Dash (Python) web app. Most of the visualisations such as charts and maps are out-of-the box Plotly javascript charts. Some I've pushed hard but, at base, I think the main map is limited as it is really just a Choropleth chart. I'd love to explore more open frameworks for map specific stuff, like Leaflet and Mapbox.

<TODO>




# Collaborator Notes


* The web application is now a stand-alone Flask app, with the Dash app embedded inside it. (Flask App(Dash App))
* 4 containers are used (webapp, certbot, nginx, datadog_agent)

## Start up
1. Manual startup will use TLS certificates contained in /infrastructure/certbot
2. Generate certs can be done by running startup-generate-certs.sh

## TLS Certificate Cycling (is manual)

Background
* Every 3 months, I have to cycle out the TLS (HTTPS) certificates.
* Presently this is a manual process as I am running an NGINX container (reverse proxy) which must have valid TLS certs 
* I'm also running a certbot container which can successfully generate new certs and inject them into NGINX, however it does not seem to be cycling them out, despite me trying to get this working with a script in the docker-compose.yml file.
* TLS certs are stored as Github secrets, and baked in during a full pipeline build
* So as long as there are valid certs as secrets, we are good, I just need to generate them.

Generating new certs
* SSH to production server
* Bring all containers down with `sudo docker stop $(sudo docker ps -a -q)`
* Check they are down with `docker ps`
* Restart all services with the appropriate script `. start-up-generate-certs.sh`
* (Note the new certs only exist in the NGINX container, so we need to extract them. It's easiest to do whilst it is running)
* Obtain the container ID for NGINX container with `docker ps`
* Copy both keys to $HOME as files 

`docker cp -L e9e73443e9f2:/etc/letsencrypt/live/worldatlas.org/privkey.pem ~/privkey.pem`

`docker cp -L e9e73443e9f2:/etc/letsencrypt/live/worldatlas.org/fullchain.pem ~/fullchain.pem`

Noting the e9e73443e9f2 above is the containerID of the nginx container

* Copy the content of each key file into GITHUB SECRETS (repo > settings > secrets > actions > ...)
* (OPTIONAL) Rebuild whole deployment by manually rerunning the github actions for `deploy` (takes 15 mins and can be a bitch)




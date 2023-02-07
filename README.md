# Welcome

**Enspired by Microsoft's Encarta World Atlas (1997), this project's mission is "to make important global datasets more accessible, for everyone"**

This is the open-sourced repository for my https://worldatlas.org concept. It's a web app that visualises thousands of open-datasets using Plotly Dash, built in Python. It's taken me around two years to build as a passion project. See my [article](https://medium.com/towards-data-science/ive-built-a-public-world-atlas-with-2-500-datasets-to-explore-8b9ae799e345) published in Towards Data Science (medium.com) for a comprehensive background, with jokes.

For those who are learning and want to discover a bit more about the capabilities of Plotly Dash and Python through this project, welcome. I've provided notes in this readme file *especially* for you. For developers who may wish to contribute and enhance my shabby codebase, also, welcome. This is my first open-source project and I don't know how it works or if anyone wants to help. I've provided lots of technical detail on how the site works in the sections below. I've also provided a roadmap (near the end) of the backlog of things I'd like to improve.

Finally, please note this is a self-funded experiment with no seed funding. I've purchased the worldatlas.org domain out of my own savings and I personally pay for all the cloud infrastructure (virtual machines, hosting, etc). I'd really love some help to try to turn this prototype into something real; something that genuinely could become a center for learning for all ages. That's the dream I guess. I've tried to demonstrate, with open-source tools in datascience, that we can engineer a generic platform to visualise data and help us learn things about the world in a way that Wikipedia just can't achieve with static text and images.

Thirty years ago we replaced the paper encyclopaedia with Wikipedia. I ask you: where is our modern replacement for the paper World Atlas? I think there is a gaping hole to fill here. Why don't we build one together as a community? Free to use and free of advertising. Forever.

Dan Baker

# Quick Start

System requirements: ~4GB memory (RAM) on your local machine.

## Run from a local machine *without* Docker 

This is the least complex way to run the app as we will spin it up directly from your local webserver on your Python kernal. However it is also fidly on some operating systems like Windows (especially if you are running Annaconda). If you're on Linux or MacOs, you should be fine.

#### 1. Clone repository to your machine 

Recommend using [Github Desktop](https://desktop.github.com/) or Git command line interface (CLI) in a terminal

`git clone git@github.com:danny-baker/atlas.git`

#### 2. Setup virtual environment 

This varies slightly between Linux, MacOS, Windows. 

`python3 -m venv venv`

`source venv/bin/activate`

#### 3. Ensure you are in the project root folder

`cd atlas` (or similar)

#### 4. Install python packages

`pip3 install -r requirements.txt`

Note you may struggle if trying to install with Annaconda with 'conda install'. This is because the site is built and tested in linux with the 'pip3' python package installer. If you get stuck here and can't use pip3 for some reason, I recommend using the Docker approach in the next section. This means the app will be built in a linux container and will run perfectly every time.

#### 5. Spin up the app in your local web browser!

`python3 wsgi.py`

This is the app entry point. The above command should start everything happening. Give it 30 seconds to spin up, and the console should spit out a URL. Copy-paste this URL into your browser and hopefully you can play with the site locally. 

<br>

## Run from a local machine *with* Docker (pull image)

This is the most reliable method to run the app as a stand-alone container on your local machine, which we pull down from the github container registry. In fact, this is how the app is deployed on the production environment. You will need to have Docker installed. If you are unfamiliar with Docker, now is the time to learn. The cool thing about this: no faffing about with virtual python environments and installing requirements.txt. All that is abstracted away and happens when the Docker image is created.

#### 1. Install Docker to your local machine

Follow the relevant pathway for your operating system, on their website [here](https://docs.docker.com/get-docker/).

#### 2. Pull docker image and run

The following command will pull (download) the pre-built Docker image of the app. This is stored in the github container registry. Once the image is pulled, docker will spin it up binding it to your HTTP port 80, so it can be viewed in a browser.

`docker run -dp 80:8050 ghcr.io/danny-baker/atlas/atlas_app:latest`

Once the container is running, you can open a browser and go to `localhost` or `http:0.0.0.0:80` or similar and it should run!

<br>

## Run from a local machine *with* Docker (build image)

If you are planning to help contribute to the project and modify the main app with a pull request, then this is the way to go. In the following steps I'll show you how I build the Docker image from the codebase. Special note that this *will not* work on an Apple M1 processor as the build process has some compiling that requires the traditional 64bit intel/amd architectures. If you're running a linux or windows 64bit machine, it should work. If you're running a non-M1 MacOs, it might work. If you're running an M1 MacOs, you're 100% screwed :)

#### 1. Install Docker to your local machine

Follow the relevant pathway for your operating system, on their website [here](https://docs.docker.com/get-docker/).

#### 2. Clone repository to your machine 

Recommend using [Github Desktop](https://desktop.github.com/) or Git command line interface (CLI) in a terminal

`git clone git@github.com:danny-baker/atlas.git`

#### 3. Build the Docker image

From a terminal in the main repo root directory

`docker build . --tag atlas_app`

This above commands will first build the main Python web application into a Docker image, based on the `Dockerfile` in the repo. It will take a good 3-5 minutes to complete but you should see a bunch of outputs in the terimal window. During this build, an Ubuntu virtualised linux operating system is utilised, and all the python modules and dependencies will be installed. The main image file is around 3GB when finished. The reason it's so large is that all of my data files are currently being containerised also, so the app has direct access to them at run-time. Totally aware there are better ways to do this, such as moving all the processed data files to S3 bucket blob storage etc.

#### 4. Run the Docker image (spin up the container)

`docker run -dp 80:8050 atlas_app`

Once the image is built, you can bring it up and view it on your local machine's web browser with the above command. The default output port for the app is `8050` so in the snippet above, we are simply binding the container's output port (8050) to your local machine's port 80 (http web traffic) so we can view the running app via a browser.


#### 5. View running container from your web browser

Once the container is running (check in docker desktop dashboard or with `docker ps` in terminal) You should just be able to open a web browser and punch in whatever the IP and port is displayed in the terminal output from Docker. This doesn't always work. Sometimes I've found this can be buggy on Docker desktop on Windows and Mac. For example if you have another running container that is already using port 80, there will be a conflict when this container comes up and tries to bind to port 80. I've also had situations where no other containers are running except my container. It's on port 80. But I open the browser and it just doesn't work. When I switched my development environment over to true linux operating system, all these problems went away.

The reality with development I have found over 2 years on this project: if the final running app is going to be deployed on a linux operating system (I.e. Ubuntu 18.04 linux server), then *develop* it on a local machine using a linux operating system, with no compromises. MacOS is good, but not perfect. Windows subsytem for linux is ok, but even less perfect. Linux is reliable and pain free, ensuring issues you solve on your local machine, will likely also be solved on the production server. Case in point: I can't even build the docker image on my M1 Mac due to a compiling issue.

# Slow Start

### What is this site?

It's an educational website (prototype) that allows you to visualise thousands of public datasets about the world. Inspired by Microsoft Encarta 1995, it's mission is to make important data more accessible, for everyone. The idea was something like a modernised replacement for the paper World Atlas, as Wikipedia replaced the paper encyclopaedia.

### What this site is not

Perfect in any way. There have been *many* tradeoffs made to experiment with some of these ideas, and I've developed it on my own so far.

### Why I built it

The internet is en ever expanding mess. Important data is scattered around the place. Most people don't have any idea where to find good data, nor how to visualise or interpret it. I've tried to find some of it (good data) and visualise it (often badly) so I could learn things. Then I thought others might find it useful to learn. I also wanted to experiment with modern tools in data science, like Plotly Dash. See my [article](https://medium.com/towards-data-science/ive-built-a-public-world-atlas-with-2-500-datasets-to-explore-8b9ae799e345) on Towards Data Science for a full white paper pitch, with jokes.

### How it works (generally)

It's essentially a Plotly Dash App on steroids (it's encased in a proper Flask app)

It acts as a generalised Python engine for ingesting county-scale geodatasets and visualising them in a variety of ways with interactive maps & charts. The idea being: it should be fun and easy to explore a dataset that interests you.

Datasets, such as Global population, are first processed and standardised for the engine to ensure things like the countries have a consistent identifier (there are many variations in country/region names and identification standards, such as United Nations M49, ISOA3 etc). I've collected over 2500 datasets and experienced the pain of different standards of identification. I also tag each dataset based on the type of data it is (continuous, quantitative, ratio etc.). For example, is the value for each country in a dataset a percentage or is it an actual number? This classiciation allows the graphs and charts to behave appropriately. This is not perfect because I'm not a statistician, but I've done a first pass to classify the various data types for thousands of datasets.

The visualisations are courtesy of Plotly Dash open-source, which provides a powerful library of interactive javascript charts.

### How it works (nerd level detail)

TODO. Talk about containers and shit.

## How to collaborate

This is my first proper open source project. I'd love some help. There is lots to do.

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




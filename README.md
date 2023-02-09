# Welcome

**Inspired by Microsoft's [Encarta World Atlas (1997)](https://www.youtube.com/watch?v=QpbrFoXPXdU), the mission of this project is "to make important global datasets more accessible, for everyone"**

This is the open-sourced repository for my [worldatlas.org](https://worldatlas.org) concept. I've tried to demonstrate what a front-end to cool data could look like, using popular open-source tools in datascience. It's a web application that visualises thousands of open-datasets using Plotly Dash, built in Python. With over 2,500 curated datasets, it's taken me around two years to build as a passion project. For a more detailed background with jokes, see my [white paper](https://medium.com/towards-data-science/ive-built-a-public-world-atlas-with-2-500-datasets-to-explore-8b9ae799e345) published in Towards Data Science (medium.com).

For those who are learning and want to discover a bit more about the capabilities of Plotly [Dash](https://dash.plotly.com/introduction) and Python through this project, welcome. I've added notes in this readme file *especially* for you. For developers who may wish to contribute and enhance my shabby codebase, also, welcome. This is my first open-source project and I don't know how it works or if anyone wants to help. I've provided lots of technical detail on how the site works in the sections below. I've also provided a backlog of things I'd like to improve.

Please note this is a self-funded experiment with no seed funding. I've purchased the worldatlas.org domain out of my own savings and I personally pay for all the cloud infrastructure (virtual machines, hosting, etc). I'd really love some help to try to turn this prototype into something real; something that could become a learning center for all ages.  

I hope you find something useful here. 

Dan Baker

P.S. Pull requests are welcomed with open arms :heart:

# Quick Start

* The following sections will outline how to spin up the app on your local machine.
* Note this is a Dash-Python app wrapped in a Flask App
* The two key Python files where the magic happen are `/flask_app/dash_app/app.py` and `/flask_app/dash_app/data_processing.py`
* Everything else is largely supporting stuff for deployment in production, and you can disregard.
* System requirements: ~4GB memory (RAM) on your local machine.

## Run from a local machine *without* Docker 

This is the least complex way to run the app as we will spin it up directly from your local webserver on your Python installation. However it is also fidly on some operating systems like Windows (especially if you are running Annaconda). If you're on Linux or MacOs, you should be fine.

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

This is the most reliable method to run the app as a stand-alone container on your local machine, which we pull down from the github container registry. This is how the app is deployed on the production environment. You will need to have Docker installed. If you are unfamiliar with Docker, now is the time to learn. The cool thing about this: no faffing about with virtual python environments and installing requirements.txt. All that is abstracted away and happens when the Docker image is created. However, note that if you plan to modify the code and do a pull-request you will need to be able to build the container image yourself (next section) or at least run the app directly from your local Python webserver (previous step). This is more for sight seeing.

#### 1. Install Docker to your local machine

Follow the relevant pathway for your operating system, on their website [here](https://docs.docker.com/get-docker/).

#### 2. Pull docker image and run

The following command will pull (download) the pre-built Docker image of the app. This is stored in the github container registry. Once the image is pulled, docker will spin it up binding it to your HTTP port 80, so it can be viewed in a browser.

`docker run -dp 80:8050 ghcr.io/danny-baker/atlas/atlas_app:latest`

Once the container is running, you can open a browser and go to `localhost` or `http:0.0.0.0:80` or similar and voilla, you will have the app running directly from your local machine.

<br>

## Run from a local machine *with* Docker (build image)

If you are planning to help contribute to the project and modify code with a pull request, then this is the way to go. In the following steps I'll show you how I build the Docker image from the codebase. Special note that this *will not* work on an Apple M1 processor as the build process has some package compiling that requires the traditional 64bit intel/amd architectures. If you're running a linux or windows 64bit machine, it should work. If you're running a non-M1 MacOs, it might work. If you're running an M1 MacOs, you're totally screwed :sob:

#### 1. Install Docker to your local machine

Follow the relevant pathway for your operating system, on their website [here](https://docs.docker.com/get-docker/).

#### 2. Clone repository to your machine 

Recommend using [Github Desktop](https://desktop.github.com/) or Git command line interface (CLI) in a terminal

`git clone git@github.com:danny-baker/atlas.git`

#### 3. Build the Docker image

From a terminal in the main repo root directory

`docker build . --tag atlas_app`

The above command will build the main Python web application into a Docker image, based on the `Dockerfile` in the repo. It will take a good 3-5 minutes to complete but you should see a bunch of outputs in the terimal window. During this build, an Ubuntu virtualised linux operating system is utilised, and all the python modules and dependencies will be installed. The main image file is around 3GB when finished. The reason it's so large is that all of my data files are currently being containerised also, so the app has direct access to them at run-time. Totally aware there are better ways to do this.

#### 4. Run the Docker image (spin up the container)

`docker run -dp 80:8050 atlas_app`

Once the image is built, you can bring it up and view it on your local machine's web browser with the above command. The default output port for the app is `8050` so in the snippet above, we are simply binding the container's output port (8050) to your local machine's port 80 (http web traffic) so we can view the running app via a browser.


#### 5. View running container from your web browser

Once the container is running (check in docker desktop dashboard or with `docker ps` in terminal) You should just be able to open a web browser and punch in whatever the IP and port is displayed in the terminal output from Docker. This doesn't always work. Sometimes I've found this can be buggy on Docker desktop on Windows and Mac. For example if you have another running container that is already using port 80, there will be a conflict when this container comes up and tries to bind to port 80. I've also had situations where no other containers are running except my container. It's on port 80. But I open the browser and it just doesn't work. When I switched my development environment over to true linux operating system, all these problems went away.

The reality with development I have found over 2 years on this project: if the final running app is going to be deployed on a linux operating system (I.e. Ubuntu 18.04 linux server), then *develop* it on a local machine using a linux operating system, with no compromises. MacOS is good, but not perfect. Windows subsytem for linux is ok, but even less perfect. Linux is reliable and pain free, ensuring issues you solve on your local machine, will likely also be solved on the production server. Case in point: I can't even build the docker image on my M1 Mac due to a compiling issue.

# Documentation

### What is this site?

It's an educational website (prototype) that allows you to visualise thousands of public datasets about the world. Inspired by Microsoft Encarta 1995, it's mission is to make important data more accessible, for everyone. The idea was something like a modernised replacement for the paper World Atlas, in the same way Wikipedia replaced the paper encyclopaedia.

### How it works (generally)

It's a Plotly Dash App encased in a proper Flask app. It acts as a generalised Python engine for ingesting county-scale geodatasets and visualising them in a variety of ways with interactive maps & charts. The idea being: it should be fun and easy to explore a dataset that interests you. The visualisations are courtesy of Plotly Dash open-source, which provides a powerful library of interactive javascript charts which are available out-of-the box in Dash web apps. 

### How it works (nerd level detail)

In the following sections I'll outline the core aspects of the system in the hope you might help me improve it. Please also note this has been a solo project, so I've cut lots of corners and kept it as lean as possible with minimal 3rd party tools and systems. For example, I do not use any SQL databases. Instead I use .csv files for metadata and .parquet (pyArrow) binary files for massive compression and super fast read of processed data.

#### 0. Core Systems

The app is hosted on a single beefy virtual machine in an Azure datacenter in the UK, with no CDN, load balancing or anything fancy. The main reason for this is I need lots of memory (RAM) as each instance of the app is 1GB (due to the large main dataframe) and I want to run a few in parallel. This ruled out app services like Heroku pretty quickly as it is ram-poor in its offerings.

The deployed app is an orchestration of 4 containers:
1. The web application (Flask-Dash container)
2. NGINX container (reverse proxy that receives incoming connections, does HTTP caching and pipes to the app)
3. Certbot container (for refreshing TLS/HTTPS certificates)
4. Datadog container (for observability and logging)

So basically when someone hits the site they first hit the NGINX container with 2 workers that can handle up to 8096 simultaneous connections (with HTTP caching), they are then routed to the underlying web app container which has 1-3 Gunicorn workers running about 5 threads each. Each thread can share the data of their parent worker, so this helps with queueing and resource optimisation. The certbot and datadog containers are just for maintenance stuff. I'm sure there are better ways to do this, but the key thing I found I needed was full hardware control of dedicated virtual machines (so I could specify my memory requirements), and this is why I've gone down this rather low-level manual path of web hosting. If there are any cloud engineer guns out there: please help.

#### 1. Data Processing

In order to build a generalised engine to ingest country-scale datasets, the key enabler is standardisation. We need to group all data for a given region in an accurate and precise way. Now you might assume (as I did) that all this would be easy. Surely, published datasets from sources like UN Data Portal, World Bank, Open-Numbers would be easy to interweave. The truth is: it's not that simple. Country and region names vary over time (borders change) and in the way they are spelt. ASCII character encoding (e.g. UTF-8) can vary and cause anomalies. Yes it's true that we have standardised unique region identifiers to solve that very problem, such as the [United Nations M49](https://unstats.un.org/unsd/methodology/m49/) integer based system (New Zealand = 554) or the International Organization for Standardisation (ISO) A3 alpha one (New Zealand = NZL). These systems are useless if your dataset hasn't been tagged with them. So a LOT of my time was spent curating the datasets, or converting between standards, or manually checking to ensure I had all data standardised to M49 integer, which is the basis for my main dataset.

I've now personally collected around 2,600 country-scale statistical datasets. I've curated them and standardised to M49 format. After data processing they are stored as an 86MB parquet binary file, which is decompressed into a 1GB dataframe in memory at run-time, which forms the backbone of the app.

 I also tag each dataset based on the type of data it is (continuous, quantitative, ratio etc.). For example, is the value for each country in a dataset a percentage or is it an actual number? This classification allows the graphs and charts to behave appropriately. This is not perfect because I'm not a statistician, but I've done a first pass to classify the various data types for thousands of datasets. If you are a statistician: I'd love some help auditing, correcting, and refining.

#### 2. Web App

blah

#### 3. Infrastructure

blah

#### 4. Deployment

blah


## Backlog

### Front end

**Expanding the mapping capabilities beyond Plotly charts**

Presently the site is built as a Flask app, wrapping a Plotly Dash (Python) web app. Most of the visualisations such as charts and maps are out-of-the box Plotly javascript charts. Some I've pushed hard but, at base, I think the main map is limited as it is really just a Choropleth chart. I'd love to explore more open frameworks for map specific stuff, like Leaflet and Mapbox.

### Back end

**Automatically update data via APIs**
Presently a big limitation is all these datasets are a snapshot in time of what I scraped a few years ago. It's not a big deal as most of these datasets are only updated every 2-4 years, but it does mean the site ages and loses data currency. Many of the data stores such as UN data portal have APIs to connect, so I think it would be cool to build a proper data processing pipeline that periodicaly polls this data and updates the app when new data is available. It would probably still need a lot of human oversight.


**Upgrading metatdata csv files to PostGres database tables**
The curation, tagging and categorisation of all datasets is presently in a giant file `/data/dataset_lookup.csv`. This is I tag each dataset by the type of data it is, and set where it sits in the overhead navigation menu, which is all constructed at run-time dynamically. It's now over 2500 rows and is pretty cumbersome to manually manage. It might be wise to convert it to proper postgres table. I'm not sure. I get by with csv for now.


**TLS Certificate Cycling (is manual)**

It would be good to get TLS certs cycling properly. Certbot container is not refreshing them. Could explore Tailscale (which now supports TLS cert generation). 

Background
* Every 3 months, I have to cycle out the TLS (HTTPS) certificates.
* Presently this is a manual process as I am running an NGINX container (reverse proxy) which must have valid TLS certs 
* I'm also running a certbot container which can successfully generate new certs and inject them into NGINX, however it does not seem to be cycling them out, despite me trying to get this working with a script in the docker-compose.yml file.
* TLS certs are stored as Github secrets, and baked in during a full pipeline build
* So as long as there are valid certs as secrets, we are good, I just need to generate them.

Generating new certs (my task list)
* SSH to production server
* Bring all containers down with `sudo docker stop $(sudo docker ps -a -q)`
* Check they are down with `docker ps`
* Restart all services with the appropriate script `. start-up-generate-certs.sh`
* (Note the new certs only exist in the NGINX container, so we need to extract them. It's easiest to do whilst it is running)
* Obtain the container ID for NGINX container with `docker ps`
* Copy both keys from running NGINX container to $HOME as files 

`docker cp -L e9e73443e9f2:/etc/letsencrypt/live/worldatlas.org/privkey.pem ~/privkey.pem`

`docker cp -L e9e73443e9f2:/etc/letsencrypt/live/worldatlas.org/fullchain.pem ~/fullchain.pem`

Noting the e9e73443e9f2 above is the containerID of the nginx container

* Copy the content of each key file into GITHUB SECRETS (repo > settings > secrets > actions > ...)
* (OPTIONAL) Rebuild whole deployment by manually rerunning the github actions for `deploy` (takes 15 mins and can be a bitch)

### Datasets

There are a ton of new datasets I'd like to bring in, that include:
* shipwrecks (how cool would it be to see shipwrecks, like the titanic on the 3d globe view)
* census data (have not yet explored this layer of granularity)

### Visualisation

* Would like to explore MapBox and some of the insane 3d visualisations we can do now, and build out the Deck.gl functionality.
* There are probably better charts for displaying much of the information.
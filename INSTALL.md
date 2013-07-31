# Phalanx Linq Installation

Phalanx Linq is Django application which is cross platform and runs on Linux, Mac OSX, Solaris, *BSD, and Windows.

The steps below describe how to install on a clean Ubuntu Virtual Machine (12.04) from Azure.

## Install Dependancies

Dependancies include Apache (webserver), mod_wsgi, python, Django, and MongoDB.

    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
    echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/10gen.list
    sudo apt-get update
    sudo apt-get install apache2 libapache2-mod-wsgi python-pip build-essential python-dev libxml2-dev libxslt-dev git mongodb-10gen

## Install Phalanx Linq

    cd /opt
    sudo mkdir phalanxlinq
    sudo chown azureuser phalanxlinq
    sudo chgrp azureuser phalanxlinq
    git clone https://github.com/osiris-x11/phalanxlinq.git
    cd phalanxlinq
    sudo pip install -r requirements.txt

## Configure MongoDB

Create data directories

    sudo mkdir /data
    sudo mkdir /data/db

Enable text search by adding the following line to /etc/mongodb.conf

    textSearchEnabled = true

Start MongoDB by either:

    sudo service mongodb restart
or

    sudo mongod --setParameter textSearchEnabled=true > /dev/null &

Verify MongoDB is running and create indexes:

    mongo
    use phalanxlinq
    db.companies.ensureIndex({ "$**" : "text" }, { "weights" : { "Name" : 10, "DBAs" : 7, "Industry.LineOfBusiness" : 3 }, "name" : "TextIndex" })
    db.companies.ensureIndex({'AnnualSalesUSD':1})
    db.companies.ensureIndex({'Flags':1})
    db.companies.ensureIndex({'Industry.SICs.Code':1})

## Add Phalanx Linq site to Apache

    sudo rm /etc/apache2/sites-enabled/000-default 
    sudo ln -s /opt/phalanxlinq/phalanxlinq/virtual-host-apache /etc/apache2/sites-enabled/000-phalanxlinq
    sudo service apache2 restart

## Initial database

There are several ways to initialize the database using D&B data. Choose the one works best for your needs.

Note: Options 2 & 3 will require setting ACCOUNT_KEY and BING_MAPS_API_KEY in phalanxlinq/settings.py. ACCOUNT_KEY is the key for D&B Developer Sandbox (https://datamarket.azure.com/dataset/dnb/developersandbox). BING_MAPS_API_KEY is the key used for geocoding using Bing Maps (https://www.bingmapsportal.com/)

### Option 1: Load static snapshot

    cd /opt/phalanxlinq
    wget http://phalanxlinq.cloudapp.net/static/companies.json
    mongoimport --db phalanxlinq --collection companies --file companies.json
    ./manage.py loader flags loadsic

### Option 2: Populate from Azure

    cd /opt/phalanxlinq
    ./manage.py loader populate consolidate geocode-bing flags loadsic

### Option 3: Populate from Azure with custom geocoder

    cd /opt/phalanxlinq
    ./manage.py loader populate consolidate geocode-google flags loadsic


# FAZ WebSCraper
This repository contains source code to download data from one of Germany's biggest and respected newspaper. It connects to the [FAZ homepage](https://www.faz.net/aktuell/) 
and downloads all articles from the website. Two options exist for saving the data:
 - write it to a JSON file
 - Setup a [MongoDB Client](https://www.mongodb.com/) by [downloading](https://www.mongodb.com/download-center) it and using the Python [pyMongo](https://api.mongodb.com/python/current/) library 
 to write the data into it. 

# Prerequisits
The source code is written in [Python 3.8](https://www.python.org/) and uses f-formatted strings. It therefore requires Python 3.6. 
The script was written on a Windows 10 machine and has only been tested on a [Rasperian OS](https://www.raspberrypi.org/downloads/raspbian/) on a Rasperry Pi.

# Installation
You can clone this repository by running:
	
	git clone https://github.com/dheinz0989/webscraper

# Requirements
As mentioned in the Introduction, in order to use the MongoDB as a database, please set it up before running the script by following the instructions in the introduction.
Furthermore, the following Python modules are used within the script:
[requests](https://pypi.org/project/requests/) is a module used to request HTML webpages and allows easy ```PUT```and ```POST``` methods
[beautifulsoup4](https://pypi.org/project/beautifulsoup4/) is a module to scrape data from a HTML web page
[tqdm](https://pypi.org/project/tqdm/) adds a progressbar for iterating tasks
[pymongo](https://pypi.org/project/pymongo/3.2/) is a client which can be used to read and write from/to a MongoDB
[pyyaml](https://pypi.org/project/pyaml/) is a module used to read and write YAML files.

In order to run the script, you need to install them prior to use it. The recommended standard approach is to [pip install](https://note.nkmk.me/en/python-pip-install-requirements/) them.

```
pip install requirements.txt
```
# Documentation
The documentation is currently written and can be found the [docs](https://github.com/dheinz0989/webscraper/blob/master/docs/build/html/WebScraper.html) directory. It is still empty and being updated

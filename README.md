#OpenCovidTrace Website

This is repository for OpenCovidTrace Website https://opencovidtrace.org
It generates by pelican https://docs.getpelican.com/en/stable/

##Requirements

Install python requirements by `pip3 install -r requirements.txt`

Install node requirements by `npm install`

##Makefile for a pelican Web site

Usage:
   make html                           (re)generate the web site
   make clean                          remove the generated files
   make regenerate                     regenerate files upon modification
   make publish                        generate using production settings
   make serve [PORT=8000]              serve site at http://localhost:8000
   make serve-global [SERVER=0.0.0.0]  serve (as root) to $(SERVER):80
   make devserver [PORT=8000]          start/restart develop_server.sh
   make stopserver                     stop local server



## OpenCovidTrace app

iOS https://github.com/OpenCovidTrace/octrace-ios

Android https://github.com/OpenCovidTrace/octrace-android
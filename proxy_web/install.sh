#!/bin/bash

sudo apt-get update -y && sudo apt-get install -y python3 && sudo apt-get install -y python3-pip
pip3 install flask
pip3 install requests
pip3 install pandas

echo "finished"

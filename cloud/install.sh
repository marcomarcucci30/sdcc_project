#!/bin/bash

sudo apt-get update -y && sudo apt-get install -y python3 && sudo apt-get install -y python3-pip
pip3 install flask
pip3 install requests
pip3 install pandas
pip3 install numpy
pip3 install mysql-connector-python
pip3 install 'scikit-learn>=0.23.2'
pip3 install imbalanced-learn
echo "finished"

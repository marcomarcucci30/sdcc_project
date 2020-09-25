#!/bin/bash
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get update -y && sudo apt-get install -y python3 && sudo apt-get install -y python3-pip
pip3 install locust

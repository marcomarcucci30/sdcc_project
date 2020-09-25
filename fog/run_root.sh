#!/bin/bash

docker --version

sudo systemctl enable docker
minikube start --driver=docker
eval "$(minikube docker-env)"
cd /home/ubuntu/ec2-user/project/fog/
docker build -t hellonode:v1 .
minikube addons enable metrics-server
cd yaml || exit
kubectl delete -f dep.yaml
kubectl delete -f ser.yaml
kubectl create -f dep.yaml
kubectl create -f ser.yaml
kubectl delete -f hpa.yaml
kubectl create -f hpa.yaml
cd .. || exit
kubectl describe services exampleservice | grep -w 'IP\|Port'
kubectl describe services exampleservice | grep -w 'IP\|Port' | grep 'IP' | awk '{print $2}' > configIpPortLoadBalancer.txt && kubectl describe services exampleservice | grep -w 'Port' | grep 'Port' | awk '{print $3}' | cut -d'/' -f 1 >> configIpPortLoadBalancer.txt
python3 /home/ubuntu/ec2-user/project/fog/proxy.py &
minikube tunnel &
echo "finished"

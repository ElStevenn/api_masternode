#!/bin/bash

# Constants
container_name="bitget_api_v4"
port=8000

# Stop and remove container
docker stop $container_name
docker rm $container_name

# Remove image
docker image rm bitget_api

# Build container
docker build -t bitget_api .

# Run container
docker run -d -p $port:8000 --name $container_name bitget_api

# Get relevant data
ip=$(docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $container_name)
host_port=$(docker inspect --format='{{(index (index .NetworkSettings.Ports "8000/tcp") 0).HostPort}}' $container_name)

echo "----------------------------------------------------"
echo "Container IP: $ip"
echo "Host Port: $host_port"
echo "Container Name: $container_name"

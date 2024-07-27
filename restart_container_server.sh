#!/bin/bash

# Constants
container_name="bitget_api_v4"
port=8000
always_restart="yes" # -v: 'yes' | 'no'

# Stop and remove container
docker stop $container_name
docker rm $container_name

# Remove image
docker image rm bitget_api

echo "Run container?(y/n)"
read input

if [[ $input != "y" ]] | [[ $always_restart == "yes" ]]; then

    # Build container
    docker build -t bitget_api .

    # Run container
    docker run -d -p $port:8000 --name $container_name bitget_api

    # Get relevant data
    ip=$(docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $container_name)
    host_port=$(docker inspect --format='{{(index (index .NetworkSettings.Ports "8000/tcp") 0).HostPort}}' $container_name)
    host=$(curl ifconfig.me)

    echo "----------------------------------------------------"
    echo "Container IP: $ip"
    echo "Host Port: 8000"
    echo "Container Name: $container_name"

    echo "Container running in http://${host}:$port" 



fi
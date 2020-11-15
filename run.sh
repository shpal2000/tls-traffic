#!/bin/bash
docker rm -f traffic_node_admin
docker network disconnect --force host traffic_node_admin
docker run --network=host --name traffic_node_admin --volume="$1:/rundir" -it -d --rm tlsjet:latest /bin/bash
docker exec -d -w /rundir traffic_node_admin python3 -m traffic_node.node_admin "$1"


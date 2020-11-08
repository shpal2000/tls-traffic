#!/bin/bash
docker run --network=host --name tlsjet_node_admin --volume="$1:/rundir" -it -d --rm tlsjet:latest python3 -m traffic_node.node_admin "$1"


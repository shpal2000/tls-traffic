#!/bin/bash

read -p 'Host Network Interface1 (Na): ' Na1
read -p 'Host Network Interface2 (Nb): ' Nb1

docker network create -d macvlan -o parent=$Na1 macvlan_${Na1}
docker network create -d macvlan -o parent=$Nb1 macvlan_${Nb1}


curdir=$(pwd)

mkdir ./db
mkdir ./log
mkdir ./cores
mkdir ./traffic
mkdir ./arenas
mkdir ./certs
mkdir ./ssh
mkdir ./lib
mkdir ./bin
mkdir ./traffic_node

curl -O -J http://10.115.78.80/tlsjet/tlsjet_docker.tar.gz
docker load --input tlsjet_docker.tar.gz
rm tlsjet_docker.tar.gz

cd ./arenas
curl -O -J http://10.115.78.80/tlsjet/arena-0.json
sed -i -e "s/IfaceNa1/$Na1/g" -e "s/IfaceNb1/$Nb1/g" -e "s/MacvlanNa1/macvlan_$Na1/g" -e "s/MacvlanNb1/macvlan_$Nb1/g" ./arena-0.json
cd ../


cd ./certs
curl -O -J http://10.115.78.80/tlsjet/tlsjet_certs.tar.gz
tar -xzvf tlsjet_certs.tar.gz
rm tlsjet_certs.tar.gz
cd ../

cd ./lib
curl -O -J http://10.115.78.80/tlsjet/tlsjet_lib.tar.gz
tar -xzvf tlsjet_lib.tar.gz
rm tlsjet_lib.tar.gz
cd ../

cd ./traffic_node
curl -O -J http://10.115.78.80/tlsjet/tlsjet_traffic_node.tar.gz
tar -xzvf tlsjet_traffic_node.tar.gz
rm tlsjet_traffic_node.tar.gz
cd ../


cd ./ssh
curl -O -J http://10.115.78.80/tlsjet/tlsjet_ssh.tar.gz
tar -xzvf tlsjet_ssh.tar.gz
rm tlsjet_ssh.tar.gz
chmod 600 *
cat ./ssh_rsa_id.pub >> ~/.ssh/authorized_keys
cat ./ssh_ecdsa_id.pub >> ~/.ssh/authorized_keys
cd ../


cd ./bin
curl -O -J http://10.115.78.80/tlsjet/tlsjet_bin.tar.gz
tar -xzvf tlsjet_bin.tar.gz
rm tlsjet_bin.tar.gz
chmod +x *
cd ../


cd $curdir
curl -O -J http://10.115.78.80/tlsjet/run.sh
chmod +x ./run.sh
$curdir/run.sh $curdir

printf "\n\nrun following command; to restart admin; if reboot vm\n\n"
printf "$curdir/run.sh $curdir\n\n"


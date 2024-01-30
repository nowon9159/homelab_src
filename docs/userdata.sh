#!/bin/bash

# apt update && install package
apt update
apt install -y net-tools

# minikube install
cat << EOF > /etc/wsl.conf
[boot]
systemd=true
EOF



#!/bin/bash


## IPtables, sysctl
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
br_netfilter
EOF

cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward                = 1
EOF

sudo sysctl --system

## Diable firewalld
systemctl stop firewalld
systemctl disable firewalld

## apt update & install required
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg
sudo apt install containerd -y

sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml > /dev/null
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
sudo systemctl restart containerd

sudo mkdir -m 755 /etc/apt/keyrings

curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.25/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.25/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt-get update

sudo apt-cache madison kubeadm

sudo apt-get install -y kubelet=1.25.0 kubeadm=1.25.0 kubectl=1.25.0

sudo apt-mark hold kubelet kubeadm kubectl

#kubeadm join 192.23.108.8:6443 --token thubfg.2zq20f5ttooz27op --discovery-token-ca-cert-hash sha256:e7755ede5d6f0bae08bca4e13ccce8923995245ca68bba5f7ccc53c9b9728cdb

kubeadm token list # $Token
openssl x509 -pubkey -in /etc/kubernetes/pki/ca.crt | openssl rsa -pubin -outform der 2>/dev/null | openssl dgst -sha256 -hex | sed 's/^.* //' # $Hash
kubectl get nodes -o wide # nodeIP

sudo kubeadm join {nodeIP:6443} --token {Token} --discovery-token-ca-cert-hash sha256:{Hash}

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

## Off swap
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

## Load necessary kernel modules
sudo modprobe overlay
sudo modprobe br_netfilter

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

sudo apt-get install -y kubelet=1.25.13-1.1 kubeadm=1.25.13-1.1 kubectl=1.25.13-1.1

sudo apt-mark hold kubelet kubeadm kubectl


# kubeadm join
sudo kubeadm join {IP:6443} --token {token} --discovery-token-ca-cert-hash {hash}

kubeadm token list # $Token
openssl x509 -pubkey -in /etc/kubernetes/pki/ca.crt | openssl rsa -pubin -outform der 2>/dev/null | openssl dgst -sha256 -hex | sed 's/^.* //' # $Hash
kubectl get nodes -o wide # nodeIP
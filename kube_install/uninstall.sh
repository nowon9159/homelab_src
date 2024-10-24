#!/bin/bash

## master node
sudo kubeadm reset
sudo rm -r /etc/cni/net.d/*
sudo rm -r ~/.kube/config

sudo systemctl restart kubelet

## worker node
sudo kubeadm reset
sudo rm -r /etc/cni/net.d/*
udo sudo rm -r /etc/kubernetes/*

sudo systemctl restart kubelet



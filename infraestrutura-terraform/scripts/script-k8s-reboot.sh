#!/bin/sh

# INICIANDO O CLUSTER E INFORMANDO O ENDPOINT DO CONTROL PLANE PARA CONEXÃO REMOTA
swapoff -a
sudo modprobe br_netfilter
sudo sysctl -w net.ipv4.ip_forward=1
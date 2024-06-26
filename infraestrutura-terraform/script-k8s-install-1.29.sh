#!/bin/sh

# INSTALANDO AS DEPENDÊNCIAS
apt-get update
apt-get install -y software-properties-common curl bash-completion nano htop vim

KUBERNETES_VERSION=v1.30
PROJECT_PATH=prerelease:/main

# ADD REPOSITÓRIO DO KUBERNETES 
curl -fsSL https://pkgs.k8s.io/core:/stable:/$KUBERNETES_VERSION/deb/Release.key |
    gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/$KUBERNETES_VERSION/deb/ /" |
    tee /etc/apt/sources.list.d/kubernetes.list

# ADD REPOSITÓRIO DO CRI-O
curl -fsSL https://pkgs.k8s.io/addons:/cri-o:/$PROJECT_PATH/deb/Release.key |
    gpg --dearmor -o /etc/apt/keyrings/cri-o-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/cri-o-apt-keyring.gpg] https://pkgs.k8s.io/addons:/cri-o:/$PROJECT_PATH/deb/ /" |
    tee /etc/apt/sources.list.d/cri-o.list

# INSTALANDO O CRI-O E OS COMPONENTES DO KUBERNETES
apt-get update
apt-get install -y cri-o kubelet kubeadm kubectl

systemctl start crio.service

swapoff -a
modprobe br_netfilter
sysctl -w net.ipv4.ip_forward=1

# HABILITANDO O BASH COMPLETION DO KUBECTL
kubectl completion bash | sudo tee -a /etc/bash_completion.d/kubectl
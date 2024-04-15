#!/bin/sh

# INICIANDO O CLUSTER E INFORMANDO O ENDPOINT DO CONTROL PLANE PARA CONEXÃO REMOTA
sudo kubeadm init --control-plane-endpoint 'adalab0.eastus.cloudapp.azure.com:6443'

# CONFIGURANDO O KUBECTL LOCAL
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# INSTALANDO O CALICO COMO CNI PLUGIN
kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.27.3/manifests/tigera-operator.yaml
# kubectl apply -f https://github.com/weaveworks/weave/releases/download/v2.8.1/weave-daemonset-k8s.yaml

# CRIANDO ALIAS K PARA O KUBECTL LOCALMENTE
echo 'alias k=kubectl' | sudo tee -a $HOME/.bashrc
echo 'complete -o default -F __start_kubectl k' | sudo tee -a $HOME/.bashrc
exec bash

# kubectl rollout restart deployment -n kube-system corednscat s    
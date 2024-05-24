# Projeto Final do Módulo 4 | Provisionamento como Código
## Objetivo Geral:

Desenvolver e implementar um módulo Terraform que provisione um ambiente contendo um serviço Dockerizado em AWS ECS ou EKS. O projeto deve demonstrar uma compreensão completa dos conceitos fundamentais de Terraform e da plataforma AWS, integrando vários serviços para fornecer uma solução robusta e escalável.

## Descrição do Projeto:

1. Provisionamento de Serviços AWS:

    - Configurar uma VPC, subnets, gateways, e tabelas de roteamento adequadas para um ambiente de produção.
    - Implementar o serviço AWS ECS ou EKS para hospedar uma aplicação em Docker, que deverá ser disponibilizada de forma automática através do código Terraform.
    - Criar e configurar serviços auxiliares como ELB (Elastic Load Balancing), RDS para bancos de dados, e S3 para armazenamento de logs ou dados estáticos.

2. Módulo Terraform:
    - Desenvolver um módulo Terraform que encapsule a lógica para lançar um serviço de contêiner, seja utilizando ECS com Fargate ou um cluster EKS.
    - O módulo deve permitir a configuração flexível dos parâmetros do serviço, incluindo configurações de rede, segurança e auto-scaling.

3. Backend e Workspace:
    - Utilizar S3 e DynamoDB como backend para gerenciar o estado do Terraform, facilitando o trabalho colaborativo entre a equipe.
    -   Configurar diferentes workspaces para simular ambientes de desenvolvimento, teste e produção, demonstrando a habilidade de gerenciar múltiplos ambientes com Terraform.

4. Documentação:
    - Fornecer documentação completa do código, incluindo comentários sobre as escolhas de configuração e instruções detalhadas sobre como inicializar e aplicar o projeto.

## Critérios de Avaliação:
- Correção Técnica: O ambiente deve ser provisionado sem erros e todas as configurações devem ser aplicadas como definido no projeto.
- Boas Práticas: Uso de boas práticas de codificação em Terraform, incluindo o uso adequado de módulos, variáveis, e estruturação do código.
- Inovação e Complexidade: Uso criativo e eficaz dos recursos do Terraform e da AWS para resolver o problema proposto.
- Documentação e Explicação: Clareza na documentação e na capacidade de explicar e justificar as escolhas feitas durante o desenvolvimento do projeto.

## Entrega Final:
- Documentação em formato markdown junto com o código.
- Apresentação ao vivo demonstrando a utilização do projeto, explicando o código e as escolhas de design.

---

# Descrição do Projeto Entregue

### Objetivo

Os scripts terraform entregues automatizam a infraestrutura básica de um cluster Kubernetes na Azure Cloud.

A infraestrutura é composta pelos seguintes componentes:
- Rede: VNET, Subnet e Network Security Group (NSG)
- Cluster: Load Balancer e 3 Máquinas Virtuais
- Provisionamento: Storage Account, Blob Container e Extension

### Detalhamento da Infraestrutura

1. O arquivo <b>main.tf</b> descreve o backend remoto para o .tfstate, bem como o provider utilizado e o Resource Group do projeto.
2. O arquivo <b>vnet.tf</b> descreve os recursos de VNET, Subnet, NSG e todos os componentes que compõe o Load Balancer.
3. O arquivo <b>vm-cluster-k8s.tf</b> descreve as VMs e seus principais componentes (Public IP e Network Interface).
    - O script utiliza o atributo <b>count</b> para definir a quantidade de VMs que compõe o cluster.
    - O script também utiliza o atributo <b>provisioner</b> do terraform para copiar alguns scripts .sh para as VMs.
4. O arquivo <b>storage.tf</b> descreve o Storage Account e o Blob Container que serão usados para armazenar o script de instalação do Kubernetes.
5. O script .sh que instala o Kubernetes (<b>script-k8s-install-1.29.sh</b>) é copiado para o Blob Container usando o recurso Storage Blob e a execução desse script ocorre por meio do recurso Virtual Machine Extension. Ambos os recuros são descritos no arquivo <b>vm-extension.tf</b>.
6. Por fim, o arquivo <b>variables.tf</b> contem as variáveis usadas nos scripts com seus valores default.

Após a criação da infraestrutura, temos o cluster de VMs com todos os componentes de software instalados (cri-o, kubelet, kubeadm e kubectl), porém a inicialização do cluster (kubeadm init) e posterior join dos workers ainda são feitos manualmente nas máquinas.

Para auxiliar essa tarefa, existe um arquivo .sh chamado <b>script-k8s-init.sh</b> que foi copiado para as VMs durante a sua criação. O arquivo contem todos os comandos para inicializar o cluster e instalar os demais componentes necessários, tais como o Plugin CNI e o Ingress Controller. 
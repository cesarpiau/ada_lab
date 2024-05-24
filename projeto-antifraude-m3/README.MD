# Projeto Final do Módulo 3 | Implementação Kubernetes para Detecção de Fraudes Bancárias
## Contexto

A equipe ACME, após implementar com sucesso um sistema de detecção de fraudes bancárias usando Docker e serviços como Redis e RabbitMQ para processamento assíncrono de transações e armazenamento em cache, agora busca melhorar a disponibilidade, escalabilidade, e resiliência deste sistema em um ambiente de produção real. Com o crescimento exponencial no volume de transações processadas, tornou-se crítico garantir que o sistema possa escalar de forma eficiente e manter alta disponibilidade, mesmo frente a falhas de componentes individuais ou picos inesperados de demanda.

## Objetivo

O projeto deste módulo consistirá na migração e adaptação do sistema existente para funcionar dentro de um cluster Kubernetes, aproveitando recursos como gerenciamento de configuração, auto-scaling, e self-healing para garantir que o sistema possa lidar com um volume crescente de transações sem degradação de performance ou disponibilidade.

## Requisitos

1. Kubernetes Cluster: Configuração de um cluster Kubernetes que hospedará todos os componentes do sistema, incluindo a aplicação de detecção de fraudes, Redis, RabbitMQ, e Minio.

2. Deployment de Serviços:
    - Crie deployments Kubernetes para cada um dos serviços mencionados, garantindo que eles possam ser escalados horizontalmente conforme necessário.
    - Utilize ConfigMaps e Secrets para gerenciar configurações sensíveis e não-sensíveis separadamente.
3. Persistência de Dados:
    - Implemente Persistent Volumes (PVs) e Persistent Volume Claims (PVCs) para garantir a persistência de dados críticos, como o armazenamento de objetos do Minio e a base de dados do Redis.
4. Network e Exposição de Serviços:
    - Defina e configure adequadamente os serviços Kubernetes (LoadBalancers, NodePorts, etc.) para garantir a comunicação eficaz entre os componentes do sistema e a exposição segura da aplicação ao mundo externo.
5. Documentação:
    - Forneça uma documentação detalhada do projeto, incluindo a arquitetura do sistema, como configurar e lançar o cluster Kubernetes, e como escalar os serviços conforme necessário.

## Entrega
O projeto deve ser entregue em um repositório no GitHub contendo todos os arquivos de configuração do Kubernetes, scripts de deploy, e a documentação. A documentação deve incluir instruções passo a passo sobre como configurar o ambiente, implantar a aplicação, e validar a implementação.

## Opcional
- Uso de Helm Charts para empacotamento das aplicações
- Implemente soluções de monitoramento e logging para acompanhar o estado do cluster e dos aplicativos, facilitando a detecção e a solução de problemas.

## Avaliação
Os projetos serão avaliados com base na correta implementação dos requisitos, na qualidade da documentação fornecida, e na eficácia com que o sistema implementado atende às demandas de escalabilidade, disponibilidade, e resiliência em um ambiente de produção real.

# Instruções para Executar o Projeto

## Estrutura do Projeto
O projeto está na pasta <b>projeto-antifraude-m3</b> do repositório.
Essa pasta contém quatro outras pastas chamadas <b>ferramentas</b>, <b>producer</b>, <b>consumer</b> e <b>api</b>, sendo que cada uma contém os arquivos YAML para subir as ferramentas utilizadas (Rabbitmq, Redis e Minio), o programa python para postar e processar as mensagens e a api para consulta dos relatório no MinIO, respectivamente.
Além dos scripts python, o projeto contém a massa de testes no formato JSON.

## Fluxo da Solução
O fluxo da solução ocorre da seguinte forma:
 - O job do <b>producer.py</b>, ao subir, faz a leitura do arquivo JSON e posta as mensagens nas filas do RabbitMQ (transacoes e antifraude).
 - O container de <b>consumer-antifraude.py</b> retira as mensagens da fila <b>antifraude</b> e analisa se a mesma é fraudulenta ou não, armazenando todas as transações em cache e atualizando o relatório (.txt) no bucket do MinIO com as transações fraudulentas.
 - Para cada conta é gerado um relatório cujo nome é o número da conta.
 - Consumida a massa de testes, o pod do producer se encerra.
 - A lista dos relatórios gerados pode ser acessada na API de relatórios.

OBS.: O código está devidamente comentado para um melhor entendimento.

## Pré-requisitos
A máquina deve ter o minikube ou o K3d instalado e o cluster deve subir com o seguinte comando:
```
minikube start --cpus=4 --memory=4g --ports="30001:30001,30002:30002,30003:30003,30004:30004"
```
O comando acima já expõe as portas necessárias para acessar os principais serviços do projeto e não necessita executar o port-forward.

Se estiver usando o K3D, o comando é:
```
k3d cluster create adalab -p 30001:30001 -p 30002:30002 -p 30003:30003 -p 30004:30004 --agents 2
```

## Executando o Projeto
1. A partir da raiz do projeto (<b>/projeto-antifraude-m3</b>) execute as ferramentas com o comando:
```
Kubectl apply -f ./ferramentas/.
```
2. O comando vai criar todos os elementos necessários, tais como configMaps, secrets, volumes e os deployments das ferramentas.
3. Se estiver usando o minikube sem expor as portas na criação do cluster, execute o comando port-forward para acessar as consoles, conforme abaixo:
```
kubectl port-forward service/rabbitmq-console 30001:15672
kubectl port-forward service/redis-console 30002:8001
kubectl port-forward service/minio-console 30003:9001
```
4. Se estiver usando o K3d, as consoles dos serviços já estarão disponíveis nos endereços abaixo:
    - RabbitMQ - http://localhost:30001
    - Redis - http://localhost:30002
    - Minio - http://localhost:30003
5. Em seguida, execute o comando abaixo para subir o producer, o consumer e a API:
```
Kubectl apply -f .\producer\producer.yaml -f .\consumer\consumer.yaml -f .\api\api.yaml
```
6. É possível acompanhar criação dos relatórios acessando a API.
7. Se estiver usando o minikube sem expor as portas na criação do cluster, execute o comando port-forward para acessar a api, conforme abaixo:
```
kubectl port-forward service/api-relatorios 30004:5000
```
8. Se estiver usando o K3d, a API já estará disponível no endereço abaixo:
    - http://localhost:30004/relatorios/
9. Para baixar o arquivo do relatório, acesse o endpoint:
    - http://localhost:30004/relatorios/<nome-do-arquivo.txt>

Obs.1: O Ingress foi implementado para ser usado com o Load Balancer da Azure e não funcionará com o Minikube ou K3d.
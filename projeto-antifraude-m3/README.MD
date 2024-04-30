# Projeto Final do Módulo 2 | Implementação Kubernetes para Detecção de Fraudes Bancárias
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

## Instruções para Executar o Projeto
### Estrutura do Projeto
O projeto está na pasta <b>projeto-antifraude-m3</b> do repositório.
Essa pasta contém quatro outras pastas chamadas <b>ferramentas</b>, <b>producer</b>, <b>consumer</b> e <b>api</b>, sendo que cada uma contém os arquivos YAML para subir as ferramentas utilizadas (Rabbitmq, Redis e Minio), o programa python para postar e processar as mensagens e a api para consulta dos relatório no MinIO, respectivamente.
Além dos scripts python, o projeto contém a massa de testes no formato JSON.

### Fluxo da Solução
O fluxo da solução ocorre da seguinte forma:
 - O job do <b>producer.py</b>, ao subir, faz a leitura do arquivo JSON e posta as mensagens nas filas do RabbitMQ (transacoes e antifraude).
 - O container de <b>consumer-antifraude.py</b> retira as mensagens da fila <b>antifraude</b> e analisa se a mesma é fraudulenta ou não, armazenando todas as transações em cache e atualizando o relatório (.txt) no bucket do MinIO com as transações fraudulentas.
 - Para cada conta é gerado um relatório cujo nome é o número da conta.
 - Consumida a massa de testes, o pod do producer se encerra.
 - A lista dos relatórios gerados podem ser acessda na API de relatórios.

OBS.: O código está devidamente comentado para um melhor entendimento.

### Pré-requisitos
A máquina deve ter o minikube instalado e o cluster deve subir com o seguinte comando:
```
minikube start adalab --memory=2g --nodes=3 --ports 30001 30002 30003 30004
```

### Executando o Projeto
1. A partir da raiz do projeto (<b>/projeto-antifraude-m3</b>) execute as ferramentas com o comando:
```
Kubectl apply -f ./ferramentas/.
```
2. O comando vai criar todos os elementos necessários, tais como configMaps, secrets, volumes e o deployments das ferramentas.
3. Em seguida, execute o comando abaixo para subir o producer, o consumer e a API:
```
Kubectl apply -f .\producer\producer.yaml -f .\consumer\consumer.yaml -f .\api\api.yaml
```
4. É possível acompanhar criação dos relatórios acessando o MinIO no endereço http://localhost:30003.
5. Também é possível consultar os relatórios que já foram enviados para o bucket na API http://localhost:30004/relatorios.
6. O endpoint http://localhost:30004/relatorios/<nome-do-arquivo.txt> baixa o arquivo do relatório.

OBS.1: A massa de testes possui 50 transações no formato JSON.

# Projeto Final do Módulo 2 | Conteinerização
## Descrição do Problema

O projeto final vai se basear no projeto do modulo anterior, mesmo as pessoas que não finalizaram o projeto passado poderão desenvolver utilizando o que foi feito.
O projeto se baseia na criação de um docker compose, com os seguintes serviços:
 - Aplicação
 - Minio
 - Redis
 - RabbitMQ

O docker compose deve conter uma orquestração dos container, onde a aplicação deve ser o ultimo container a subir, garantindo assim que quando subir a aplicação não encontre nenhum error.
 - Volume para persistir os dados do container do Minio, Redis e Rabbit.
 - Criação de uma network e expor apenas as portas necessárias.
 - Criação de um dockerfile para a aplicação.

Pense que é uma aplicação que deve ter como preocupação uma alta disponibilidade e que seja resiliente.
A entrega pode ser feita através de um repositório como o GitHub. Deve conter:

 - Uma documentação de como funciona o seu software
 - Quais os comandos necessário para executar a solução
 - Todos os arquivos: Lógica da aplicação, Dockerfile e um docker compose.
Lembre que toda solução deve esta contida no repositório , sem nenhuma ação previa no host que vai executar a solução.

### Relatório  
 - Deve ser um arquivo (txt, pdf, ...) 
 - Conter dados da ultima transação 
 - Deve conter o numero da conta 
 - Opcional (dados da transação previa)
 - Voce pode utilizar outras ferramentas similares de mensageiria, cache e storage.

## Instruções para Executar o Projeto
### Estrutura do Projeto
O projeto está na pasta <b>projeto-antifraude</b> do repositório.
Essa pasta contém três outras pastas chamadas <b>producer</b>, <b>consumer</b> e <b>api</b>, sendo que cada uma contém o script python para postar e processar as mensagens e a api para consulta dos relatório no MinIO, respectivamente.
Além dos scripts python, o projeto contém a massa de testes no formato JSON e o Docker Compose para a subida orquestrada dos containers.
Foram utilizadas no projeto as ferramentas RabbitMQ, Redis, MinIO, Flask e Traefik.

### Fluxo da Solução
O fluxo da solução ocorre da seguinte forma:
 - O comando <b>docker compose up -d</b> compila as imagens e executa todos os containers necessários.
 - O container de <b>producer.py</b>, ao subir, faz a leitura do arquivo JSON e posta as mensagens nas filas do RabbitMQ (transacoes e antifraude).
 - O container de <b>consumer-antifraude.py</b> retira as mensagens da fila <b>antifraude</b> e analisa se a mesma é fraudulenta ou não, armazenando todas as transações em cache e atualizando o relatório (.txt) no bucket do MinIO com as transações fraudulentas.
 - Para cada conta é gerado um relatório cujo nome é o número da conta.
 - Consumida a massa de testes, o container do producer se encerra.
 - A lista dos relatórios gerados podem ser acessda na API disponível em http://api.localhost:5000/relatorios.
 - O endpoint http://api.localhost:5000/relatorios/<nome-do-arquivo.txt> retorna a URL para baixar o relatório.

OBS.: O código está devidamente comentado para um melhor entendimento.

### Pré-requisitos
A máquina deve ter o Docker instalado.

### Executando o Projeto
1. Execute o script bash de subida dos containers com as ferramentas e instação dos pacotes python utilizados, chamado <b>docker_scripts.sh</b>.
2. Em seguinda, execute o script python <b>consumer-antifraude.py</b>, localizado na pasta consumer.
3. Em outra janela de terminal, execute o script python <b>producer.py</b>, localizado na pasta producer.
4. Por fim, retorne para janela onde está sendo executado o producer, aguarde ele terminar de processar as mensagens e interrompa o script utilizando as teclas CTRL+C.

OBS.1: O producer tem um temporizador de 0.1 segundo entre cada postagen na fila, para melhorar a visualização do processamento das mensagens.
    
OBS.2: A massa de testes possui 50 transações no formato JSON.

# Projeto Final do Módulo 1 | Mensageria, Cache e Armazenamento de Objetos
## Descrição do Problema

Desenvolver um sistema que detecta possíveis transações bancárias fraudulentas de forma assíncrona ou tempo real, utilizando análise de dados de transações, cache para acesso rápido a dados frequentemente utilizados. Caso uma transação seja definida como fraudulenta, devera ser possível fazer download de um relatório. O link deve estar disponível em um sistema de cache. 
 - Implementação persistente nao eh necessária.
 - Implementação de Dead Dead-Letter Queue (DLQ) nao e' obrigatório
 - Toda implementação deve funcionar se for necessário recriar o RabbitMQ (ou qualquer outra ferramenta), por exemplo. Vou rodar a aplicação em uma maquina virtual "zerada". 
 - Nao e' obrigatório implementar nada apos uma transação ser considerada como normal (nao fraudulenta)
 
### Relatório  
 - Deve ser um arquivo (txt, pdf, ...) 
 - Conter dados da ultima transação 
 - Deve conter o numero da conta 
 - Opcional (dados da transação previa)
 - Voce pode utilizar outras ferramentas similares de mensageiria, cache e storage.

## Instruções para Executar o Projeto
### Estrutura do Projeto
O projeto está na pasta <b>projeto</b> do repositório.
Essa pasta contém duas outras pastas chamadas <b>producer</b> e <b>consumer</b>, sendo que cada uma contém o script python para postar e processar as mensagens, respectivamente.
Além dos scripts python, o projeto contém a massa de testes no formato JSON e o script de subida dos containers com as ferramentas utilizadas e de instação dos pacotes python utilizados.
Foram utilizadas no projeto as ferramentas RabbitMQ, Redis e MinIO.

### Fluxo da Solução
O fluxo da solução ocorre da seguinte forma:
 - O script <b>producer.py</b> faz a leitura do arquivo JSON e posta as mensagens em duas filas do RabbitMQ (transacoes e antifraude).
 - O script <b>consumer-antifraude.py</b> retira as mensagens da fila <b>antifraude</b> e analisa se a mesma é fraudulenta ou não, armazenando todas as transações em cache e alimentando um arquivo local com as transações fraudulentas.
 - Consumida a massa de testes, o usuário deve interromper a execução do script <b>consumer-antifraude.py</b> utilizando CTRL+C.
 - Essa interrupção dispara a função que salva o relatório com as transações fraudulentas no bucket do MinIO e gera o link pré-assinado para download.

OBS.: O código está devidamente comentado para um melhor entendimento.

### Pré-requisitos
A máquina deve ter o Docker e o Python instalados, além do pip para a instalações dos pacotes Python.

### Executando o Projeto
1. Execute o script bash de subida dos containers com as ferramentas e instação dos pacotes python utilizados, chamado <b>docker_scripts.sh</b>.
2. Em seguinda, execute o script python <b>consumer-antifraude.py</b>, localizado na pasta consumer.
3. Em outra janela de terminal, execute o script python <b>producer.py</b>, localizado na pasta producer.
4. Por fim, retorne para janela onde está sendo executado o producer, aguarde ele terminar de processar as mensagens e interrompa o script utilizando as teclas CTRL+C.

OBS.1: O producer tem um temporizador de 0.1 segundo entre cada postagen na fila, para melhorar a visualização do processamento das mensagens.
    
OBS.2: A massa de testes possui 50 transações no formato JSON.
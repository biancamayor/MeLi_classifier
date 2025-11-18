# 📦 MeLi Classifier: Ecossistema de Engenharia de Dados & NLP

Uma solução de ponta a ponta para extração, processamento e análise de sentimentos de reviews do Mercado Livre, orquestrada via Airflow.

## 🧠 O Que Este Projeto Faz? (Para Leigos e Especialistas)

Imagine que você quer saber se um produto no Mercado Livre é bom ou ruim, mas ele tem milhares de comentários. Ler um por um é impossível.

O MeLi Classifier automatiza esse processo de forma inteligente e escalável:

1) Busca todos os comentários de um produto automaticamente.

2) Lê e Interpreta cada comentário usando Inteligência Artificial (não apenas palavras-chave, mas entendendo o contexto e a ironia).

3) Classifica se o sentimento é Positivo ou Negativo.

3) Gera um Dashboard com métricas de confiança e exemplos práticos.

A grande diferença? Isso não roda tudo num único script no meu computador. É um sistema complexo onde cada tarefa é feita por um "robô" (container) diferente, todos coordenados por um "gerente" (Airflow) na nuvem.

## 🏗️ A Arquitetura (Por Que é Complexo?)

A maioria dos projetos de dados iniciantes são "monólitos": um único arquivo Python que faz tudo. Se o scraping falhar, a análise para. Se o modelo de IA for pesado, o site trava.

Este projeto adota uma Arquitetura de Engenharia de Dados Profissional:

1. Desacoplamento Total (Microsserviços)

Em vez de um programa gigante, temos 3 programas independentes:

    - O Dashboard (Frontend): Apenas mostra dados. Não processa nada pesado.

    - O Scraper (Worker 1): Especialista em ir à web e buscar dados brutos.

    - O Analisador (Worker 2): Um computador potente com GPU/CPU dedicada apenas para rodar modelos pesados de IA (BERT).

2. Orquestração (O "Cérebro")

Usamos o Apache Airflow, a ferramenta padrão da indústria para pipelines de dados. Ele decide quando ligar cada robô, verifica se eles terminaram com sucesso e tenta novamente em caso de falha.

3. Data Lake (A "Memória")

Nada fica salvo "na máquina". Tudo vai para a nuvem (AWS S3). Isso garante que os dados persistam mesmo que os servidores sejam destruídos e recriados (o que acontece a cada execução).

## 🚀 Tecnologias e Decisões Técnicas

- **🕷️ Extração de Dados (Scraper)**

- Desafio: O Mercado Livre tem estruturas HTML complexas e dinâmicas.

- Solução: Script Python resiliente que navega por paginação, trata erros de rede e normaliza os dados brutos antes de enviar para o Data Lake.

- **🧠 Inteligência Artificial (Analyzer)**

- Desafio: Análise de sentimento tradicional (baseada em palavras positivas/negativas) falha em português (ex: "Não gostei nada" tem a palavra "gostei").

- Solução: Uso do BERTimbau, um modelo Transformer (estado da arte em NLP) pré-treinado especificamente em português brasileiro pela NeuralMind. Ele entende contexto, negação e sarcasmo.

- **⚙️ Engenharia (Docker & Airflow)**

- Docker-in-Docker: Uma técnica avançada onde o Airflow não executa o código Python diretamente. Ele usa o DockerOperator para criar, executar e destruir containers inteiros para cada tarefa. Isso garante isolamento total de dependências (o Scraper não precisa ter o PyTorch instalado, e o Analyzer não precisa de bibliotecas web).


## 📂 Estrutura do Repositório

- **airflow/:** Contém as DAGs (os "mapas" do fluxo de trabalho) que dizem ao Airflow o que fazer.

- **analyzer-app/:** O código do modelo de IA. Possui seu próprio Dockerfile e requirements.txt (pesado, com PyTorch).

- **scraper-app/:** O código de coleta de dados. Possui seu próprio Dockerfile (leve).

- **streamlit_app/:**  O site em Streamlit. Possui lógica de "polling" para verificar no S3 se os dados já estão prontos.

- **docker-compose.yml:** O maestro que sobe toda a infraestrutura localmente (Banco de dados, Webserver, Scheduler e Frontend).


## 🔄 Fluxo de Dados

- **Trigger:** usuário insere o ID do produto.
- **Verificação:** o sistema checa no S3 se o resultado já existe.
- **Orquestração:** se não existir, o Streamlit aciona o Airflow.
- **Extração (EL):** o *scraper-app* coleta dados e salva no Raw.
- **Transformação (T):** o *analyzer-app* aplica BERT e grava o JSON final.
- **Visualização:** o Dashboard lê o arquivo e exibe métricas e gráficos.

## 🛠️ Tech Stack

### Infraestrutura & Orquestração
- Docker + Docker Compose  
- Apache Airflow 3.0  
- AWS S3 (Data Lake)

### Microsserviços
- **Scraper:** Python, Requests, BS4  
- **Analyzer:** Python, PyTorch, Transformers (BERTimbau)  
- **Dashboard:** Streamlit

## 🚀 Como Executar Localmente

### Pré-requisitos
- Docker Desktop instalado e rodando + Docker Compose  
- Bucket S3 configurado  
- Credenciais AWS exportadas no ambiente com permissão de leitura/escrita em um bucket S3.


### Passo 1 — Clonar o repositório
```bash
git clone https://github.com/biancamayor/MeLi_classifier.git
cd MeLi_classifier
```

### Passo 2 — Exportar credenciais

**Linux/Mac**
```bash
export AWS_ACCESS_KEY_ID=sua_chave
export AWS_SECRET_ACCESS_KEY=sua_senha
```

**Windows (PowerShell)**
```ps1
$env:AWS_ACCESS_KEY_ID="sua_chave"
$env:AWS_SECRET_ACCESS_KEY="sua_senha"
```

### Passo 3 — Construa os Workers: Precisamos criar as imagens dos "robôs" que o Airflow vai usar
```bash
cd scraper-app && docker build -t scraper-app:latest . && cd ..
cd analyzer-app && docker build -t analyzer-app:latest . && cd ..
```

### Passo 4 — Subir o ambiente
```bash
docker-compose up --build
```

### Passo 5 — Configurar Airflow
- Acesse **http://localhost:8081**  
  Login: `seulogin` / Senha: `suasenha`
- Vá em *Admin → Variables*  
- Adicione:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
- Ative a DAG `meli_orchestrator`

### Passo 6 — Usar o Streamlit
Acesse: **http://localhost:8501**

Insira um ID de produto (ex.: `MLB-12345678`) e acompanhe o pipeline rodar.

## 📂 Estrutura do Projeto

```
├── airflow/               
│   └── dags/
│       └── orchestrator.py
├── local-airflow/
|   └── Dockerfile.airflow
|   └── requirements.txt         
├── analyzer-app/          
│   ├── src/
|   |   └── bertimbau_classifier.py
│   ├── analyze.py
│   └── Dockerfile
|   └── requirements.txt
├── scraper-app/           
│   ├── scraper.py
│   └── Dockerfile
|   └── requirements.txt
├── streamlit_app/         
│   ├── app.py
│   └── Dockerfile
|   └── requirements.txt
└── docker-compose.yml
```

## ✨ Destaques e Aprendizados

- **Docker-in-Docker:** Airflow executa containers isolados via DockerOperator.  
- **Gerenciamento de Estado:** Streamlit com polling inteligente.  
- **Resiliência:** tratamento robusto de erros de rede, API e permissões AWS.

## 📞 Contato

Desenvolvido por **Bianca**  
💼 LinkedIn: https://www.linkedin.com/in/bianca-mayor 
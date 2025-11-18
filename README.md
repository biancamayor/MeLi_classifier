📦 MeLi Classifier: Pipeline de Engenharia de Dados & NLP

Uma solução de ponta a ponta para extração, processamento e análise de sentimentos de reviews do Mercado Livre, orquestrada via Airflow.

🧠 Sobre o Projeto

O MeLi Classifier não é apenas um analisador de sentimentos; é um projeto focado em Engenharia de Dados e Arquitetura de Microsserviços.

O objetivo é extrair comentários de produtos do Mercado Livre, processá-los utilizando o estado da arte em Processamento de Linguagem Natural (NLP) para o português (BERTimbau) e apresentar insights valiosos sobre a percepção dos consumidores.

Diferente de scripts monolíticos, este projeto separa responsabilidades em containers isolados, utiliza um Data Lake (S3) para armazenamento e orquestra todo o fluxo de dados com Apache Airflow.

🏗️ Arquitetura do Pipeline

O sistema foi desenhado seguindo o padrão de Pipeline de Dados, onde cada etapa é isolada e escalável.

graph LR
    User((Usuário)) -->|Insere ID| Streamlit[🖥️ Dashboard Streamlit]
    Streamlit -->|Verifica Cache| S3[(☁️ AWS S3 Data Lake)]
    
    subgraph "Orquestração (Docker/Airflow)"
    Streamlit -.->|Dispara via API| Airflow[⚙️ Apache Airflow Scheduler]
    Airflow -->|DockerOperator| Scraper[🕷️ Container Scraper]
    Airflow -->|DockerOperator| Analyzer[🧠 Container Analyzer BERT]
    end
    
    Scraper -->|Extrai Dados| Web[Mercado Livre]
    Scraper -->|Salva Raw CSV| S3
    
    Analyzer -->|Lê Raw CSV| S3
    Analyzer -->|Processa (NLP)| BERT[Modelo BERTimbau]
    Analyzer -->|Salva Processed JSON| S3
    
    S3 -->|Lê JSON Final| Streamlit


🔄 Fluxo de Dados

Trigger: O usuário insere um ID de produto no Dashboard.

Verificação: O sistema verifica no S3 se a análise já existe.

Orquestração: Se não existir, o Streamlit aciona a API do Airflow.

Extração (EL): O Airflow inicia o container scraper-app, que coleta os dados brutos e salva na camada Raw do S3.

Transformação & Enriquecimento (T): O Airflow inicia o container analyzer-app. Este baixa os dados brutos, aplica o modelo de Deep Learning (BERT) para classificar cada comentário e salva os resultados agregados na camada Processed do S3.

Visualização: O Streamlit lê o arquivo processado final e exibe os gráficos e métricas.

🛠️ Tech Stack

Infraestrutura & Orquestração

Docker & Docker Compose: Para containerização total da aplicação e ambiente local reprodutível.

Apache Airflow 3.0: Para agendamento, orquestração e monitoramento das tarefas (DAGs).

AWS S3: Atua como Data Lake, armazenando dados brutos (.csv) e processados (.json).

Aplicações (Microsserviços)

Scraper App: Python, BeautifulSoup4, Requests. Responsável pela coleta de dados resiliente.

Analyzer App: Python, PyTorch, Transformers (Hugging Face). Implementa o modelo BERTimbau (NeuralMind), específico para o português brasileiro.

Dashboard App: Streamlit. Interface reativa que consome dados do S3 e interage com a API do Airflow.

🚀 Como Executar Localmente

Pré-requisitos

Docker e Docker Compose instalados.

Uma conta na AWS com um Bucket S3 criado.

Chaves de acesso AWS (AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY) com permissão de leitura/escrita no S3.

Passo a Passo

Clone o repositório:

git clone [https://github.com/seu-usuario/meli-classifier.git](https://github.com/seu-usuario/meli-classifier.git)
cd meli-classifier


Configure as Credenciais:
O docker-compose espera que você tenha suas credenciais exportadas no terminal ou em um arquivo .env.

# Linux/Mac
export AWS_ACCESS_KEY_ID=sua_chave
export AWS_SECRET_ACCESS_KEY=sua_senha

# Windows (PowerShell)
$env:AWS_ACCESS_KEY_ID="sua_chave"
$env:AWS_SECRET_ACCESS_KEY="sua_senha"


Construa as Imagens das Tarefas:
Como o Airflow roda containers dentro do Docker, precisamos buildar as imagens dos workers primeiro.

cd scraper-app && docker build -t scraper-app:latest . && cd ..
cd analyzer-app && docker build -t analyzer-app:latest . && cd ..


Inicie o Ambiente:

docker-compose up --build


Configure o Airflow:

Acesse http://localhost:8081 (Login: admin / Senha: admin).

Vá em Admin -> Variables.

Adicione AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY com suas credenciais (para que os workers do Airflow possam acessar o S3).

Ative a DAG meli_orchestrator (botão "ON").

Use a Aplicação:

Acesse o Dashboard em http://localhost:8501.

Insira um ID de produto (ex: MLB-12345678) e veja a mágica acontecer!

📂 Estrutura do Projeto

├── airflow/               # Configurações e DAGs do Airflow
│   └── dags/
│       └── orchestrator.py  # A "receita" do pipeline
├── airflow-local/         # Dockerfile customizado do Airflow 3.0
├── analyzer-app/          # Microsserviço de Análise (BERT)
│   ├── src/               # Código fonte do modelo
│   ├── analyze.py         # Script principal
│   └── Dockerfile
├── scraper-app/           # Microsserviço de Scraping
│   ├── scrape.py          # Script de coleta
│   └── Dockerfile
├── dashboard-app/         # Frontend Streamlit
│   ├── streamlit_app.py   # Interface do usuário
│   └── Dockerfile
└── docker-compose.yml     # Orquestração local dos serviços


✨ Destaques e Aprendizados

Docker-in-Docker: Implementação do DockerOperator permitindo que o Airflow suba containers efêmeros para cada tarefa, garantindo isolamento total de dependências (ex: o Scraper não precisa das bibliotecas pesadas de ML do Analyzer).

Gestão de Estado: O Streamlit implementa uma lógica de "polling" inteligente, aguardando o término do pipeline no Airflow antes de exibir os dados.

Tratamento de Erros: O sistema lida robustamente com erros de API, falhas de conexão e permissões AWS.

📞 Contato

Desenvolvido por Bianca.
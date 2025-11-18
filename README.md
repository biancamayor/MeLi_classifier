# 📦 MeLi Classifier: Pipeline de Engenharia de Dados & NLP

Uma solução de ponta a ponta para extração, processamento e análise de sentimentos de reviews do Mercado Livre, orquestrada via Airflow.

## 🧠 Sobre o Projeto

O **MeLi Classifier** é um pipeline completo de Engenharia de Dados aliado a técnicas modernas de NLP.

O objetivo é extrair comentários de produtos do Mercado Livre, processá-los utilizando modelos avançados em português (BERTimbau) e entregar insights claros sobre a percepção dos consumidores.

Diferente de scripts monolíticos, este projeto segue uma mentalidade de microsserviços, usando containers independentes, Data Lake no S3 e orquestração com Apache Airflow.

## 🏗️ Arquitetura do Pipeline

```mermaid
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
```

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
- Docker + Docker Compose  
- Bucket S3 configurado  
- Credenciais AWS exportadas no ambiente  

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

### Passo 3 — Build das imagens
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
  Login: `admin` / Senha: `admin`
- Vá em *Admin → Variables*  
- Adicione:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
- Ative a DAG `meli_orchestrator`

### Passo 6 — Usar o Dashboard
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
💼 LinkedIn: https://www.linkedin.com/in/bianca-mayor lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3BqS8%2FhYdnRCCTOI1BzOd%2F1Q%3D%3D

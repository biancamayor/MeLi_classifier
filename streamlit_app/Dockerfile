# 1. Imagem Base
FROM python:3.10-slim

# 2. Definir o Diretório de Trabalho
WORKDIR /app

# 3. Copiar e Instalar as Dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar o Código da Aplicação
COPY app.py .

# 5. Expor a Porta
# O Streamlit roda na porta 8501 por padrão
EXPOSE 8501

# 6. Comando para Rodar o App
# Usamos CMD aqui porque este é um container de "serviço" (longa duração).
# O --server.address=0.0.0.0 permite que ele seja acessado de fora do container.
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

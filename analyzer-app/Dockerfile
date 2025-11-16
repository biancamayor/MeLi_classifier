FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY analyze.py .

# Copia seu código fonte (onde está o bertimbau_classifier.py)
COPY src/ ./src/

# 5. Definir o Ponto de Entrada (Entrypoint)
ENTRYPOINT ["python", "analyze.py"]

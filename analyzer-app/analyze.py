from src.bertimbau_classifier import SentimentClassifier
import pandas as pd
import os
import sys
import boto3
from io import StringIO
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    from src.bertimbau_classifier import SentimentClassifier
except ImportError:
    print("Erro: Não foi possível encontrar 'bertimbau_classifier'.")
    print("Certifique-se que o arquivo 'src/bertimbau_classifier.py' existe.")
    sys.exit(1)


def read_csv_from_s3(s3_uri, csv_sep):
    """Lê um arquivo CSV de um URI S3 para um DataFrame."""
    try:
        if not s3_uri.startswith("s3://"):
            raise ValueError("URI de entrada deve começar com 's3://'")
        
        bucket, key = s3_uri.replace("s3://", "").split("/", 1)
        s3_client = boto3.client('s3')
        
        print(f"Lendo arquivo de s3://{bucket}/{key}")
        response = s3_client.get_object(Bucket=bucket, Key=key)
        
        body = response['Body'].read().decode('utf-8')
        
        return pd.read_csv(StringIO(body), sep=csv_sep)

    except Exception as e:
        print(f"Erro ao ler do S3: {e}")
        raise



def save_json_to_s3(data_dict, s3_uri):
    """Salva um dicionário python como JSON em um local S3."""
    try:
        if not s3_uri.startswith("s3://"):
            raise ValueError("URI de saída deve começar com 's3://'")
            
        bucket, key = s3_uri.replace("s3://", "").split("/", 1)
        
        print(f"Iniciando salvamento de JSON em s3://{bucket}/{key}...")
        
        json_buffer = json.dumps(data_dict, indent=4, default=str)
        
        s3_client = boto3.client('s3')
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json_buffer,
            ContentType='application/json'
        )
        print(f"Arquivo JSON salvo com sucesso em {s3_uri}")

    except Exception as e:
        print(f"Erro ao salvar JSON no S3: {e}")
        raise


def process_and_aggregate(df, classifier):
    """
    Executa a lógica de classificação e agregação.
    Retorna um dicionário com os resultados.
    """
    
    product_title = df['product_name'].iloc[0] if 'product_name' in df.columns and not df.empty else "Produto Desconhecido"
    df_comments = df[['comment', 'rating']]
    
    positives = 0
    negatives = []
    scores = []

    total_comments = len(df_comments)
    
    if total_comments == 0:
        print("Nenhum comentário para processar.")
        return {'positives_percent': 0, 
                'product_name': product_title, 
                'confidence': 0, 
                'negatives': [], 
                'total_comments': 0}
    else:
        for n_comment, comment in df_comments.iterrows():
            text = comment['comment']
            rating = comment['rating']

            if text not in ('Nan', 'nan', 'None', None) and not pd.isna(text):
                try:
                    result = classifier.predict(text=text, rating=rating)
                    score = result['score']
                    scores.append(score) 

                    if result["label"] == "POSITIVE" and result['score'] >= 70:
                        positives += 1
                    else:
                        negatives.append(text)
                except Exception as e:
                    print(f"Erro ao classificar: {e}")
                    negatives.append(text) 

        positives_percent = (positives / total_comments) * 100 if total_comments != 0 else 0
        confidence_avg = sum(scores) / len(scores) if len(scores) != 0 else 0
        confidence_avg = float(f"{confidence_avg:.2f}")

        
        return {'positives_percent': positives_percent, 
                'product_name': product_title, 
                'confidence': confidence_avg, 
                'negatives': negatives, 
                'total_comments': total_comments}



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analisador de sentimentos.")
    parser.add_argument(
        "--input-uri",
        type=str,
        required=True,
        help="Caminho S3 de entrada do arquivo CSV (ex: s3://.../raw/reviews.csv)"
    )
    parser.add_argument(
        "--output-uri",
        type=str,
        required=True,
        help="Caminho S3 de saída para o arquivo JSON (ex: s3://.../processed/results.json)"
    )
    
    args = parser.parse_args()

    print("Carregando o modelo classificador...")
    try:
        classifier = SentimentClassifier()
    except Exception as e:
        print(f"Falha ao carregar o SentimentClassifier: {e}")
        sys.exit(1)
    print("Modelo carregado.")

    raw_df = read_csv_from_s3(args.input_uri, csv_sep='█')
    
    if raw_df is not None and not raw_df.empty:
        results_dict = process_and_aggregate(raw_df, classifier)
        save_json_to_s3(results_dict, args.output_uri)
    else:
        print("Nenhuma review encontrada no arquivo de entrada.")

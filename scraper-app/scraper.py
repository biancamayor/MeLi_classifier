import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import argparse 
import boto3   
from io import StringIO 


def scrape_reviews(product_id):
    reviews_list = []

    
    headers = {
    "accept": "application/json",
    "accept-encoding": "gzip, deflate",
    "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 OPR/119.0.0.0"
    }

    product_url = f"https://produto.mercadolivre.com.br/{product_id}"
    response = requests.get(url=product_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("h1", class_="ui-pdp-title").text

    offset = 0
    limit = 15
    product_id_clean = product_id.replace('-', '') 

    while True:
        reviews_url = f"https://produto.mercadolivre.com.br/noindex/catalog/reviews/{product_id_clean}/search?objectId={product_id_clean}&siteId=MLB&isItem=true&offset={offset}&limit={limit}&x-is-webview=false"

        request = requests.get(reviews_url, headers=headers)
        soup = BeautifulSoup(request.content, 'html.parser')

        if request.status_code != 200:
            print(f"Erro na requisição({request.status_code}):{request.text}")
            break

        if soup.get_text() != None:
            try:
                review_elements = json.loads(soup.get_text())['reviews']
            except json.JSONDecodeError:
                print("Erro ao decodificar JSON. Resposta do servidor:", soup.get_text())
                break
        else:
            print("Resposta vazia do servidor")
            break 

        if len(review_elements) == 0:
            print("Não há mais comentários para carregar.")
            df = pd.DataFrame(reviews_list)
            if not df.empty:
                df['product_name'] = title
            return df 

        else:
            for review in review_elements:
                comment = None
                
                try:
                    comment = review['comment']['content']['text'].strip()
                except KeyError:
                    pass
                
                if comment != None and comment != '':
                    rating = review["rating"]
                    date = review["comment"]["date"]
                    reviews_list.append({"rating": rating, "date": date, "comment": comment})

            offset += limit
    

    print("Saindo do loop de scraping.")
    df = pd.DataFrame(reviews_list)
    if not df.empty:
        df['product_name'] = title
    return df


def save_df_to_s3(df, s3_uri):
    """Salva um DataFrame pandas em um local S3 no formato CSV (sep='█')."""
    if df.empty:
        print("DataFrame está vazio. Nenhum arquivo será salvo no S3.")
        return

    try:
        print(f"Iniciando salvamento em {s3_uri}...")
        
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False, sep='█')
        
        if not s3_uri.startswith("s3://"):
            raise ValueError("URI de saída deve começar com 's3://'")
            
        bucket, key = s3_uri.replace("s3://", "").split("/", 1)
        
        s3_client = boto3.client('s3')
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=csv_buffer.getvalue()
        )
        print(f"Arquivo salvo com sucesso em {s3_uri}")

    except Exception as e:
        print(f"Erro ao salvar no S3: {e}")
        raise





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scraper de reviews do Mercado Livre.")
    parser.add_argument(
        "--product-id",
        type=str,
        required=True,
        help="ID do produto no Mercado Livre (ex: MLB-123456)"
    )
    parser.add_argument(
        "--output-uri",
        type=str,
        required=True,
        help="Caminho S3 de saída para o arquivo CSV (ex: s3://meu-bucket/raw/produto.csv)"
    )
    
    args = parser.parse_args()

    print(f"Iniciando scraping para o produto: {args.product_id}")
    reviews_df = scrape_reviews(product_id=args.product_id)
    
    if reviews_df is not None and not reviews_df.empty:
        save_df_to_s3(reviews_df, args.output_uri)
    else:
        print("Nenhuma review encontrada ou erro no scraping.")


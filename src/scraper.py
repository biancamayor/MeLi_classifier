import requests
import time
import random
import csv
from utils import load_json_file

proxy_data = load_json_file('config\proxies.json')
random_proxy = random.choice(proxy_data['proxies'])
proxies = {"http": random_proxy['http']}
headers = load_json_file('config\headers.json')
headers["referer"]=f"https://produto.mercadolivre.com.br/{id}"

id = 'MLB3622788359'
base_url = f"https://produto.mercadolivre.com.br/noindex/catalog/reviews/{id}/search"

offset = 0
limit = 15

with open("data/reviews.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Rating", "Data", "Comentário"])

    while True:
        params = {
            "objectId": id,
            "siteId": "MLB",
            "isItem": "true",
            "offset": offset,
            "limit": limit,
            "x-is-webview": "false",
            "source_platform": "/web/mobile",
            "device_id_variant": "9e348d92-101d-4900-8ab4-8bc56633cc0f"
        }

        print(f"Buscando comentários: offset {offset}")
        response = requests.get(base_url, headers=headers, params=params, proxies=proxies)

        if response.status_code != 200:
            print(f"Erro na requisição: {response.status_code}")
            break

        data = response.json()
        reviews = data.get("reviews", [])

        if not reviews:
            print("Nenhum comentário novo encontrado. Fim da paginação.")
            break

        for review in reviews:
            rating = review.get("rating", "")
            date = review.get("comment", {}).get("date", "")
            comment = review.get("comment", {}).get("content", {}).get("text", "")
            writer.writerow([rating, date, comment.strip() if comment else ""])

        offset += limit
        time.sleep(0.5)  
1
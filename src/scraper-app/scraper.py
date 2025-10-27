import requests
from bs4 import BeautifulSoup
import json
import pandas as pd


def scrape_reviews(product_id):
    reviews_list = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json'
    }


    product_url = f"https://produto.mercadolivre.com.br/{product_id}"
    response = requests.get(url=product_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("h1", class_="ui-pdp-title").text

    
    offset=0
    limit=15

    product_id = product_id.replace('-', '')

    while True:
        
        reviews_url = f"https://produto.mercadolivre.com.br/noindex/catalog/reviews/{product_id}/search?objectId={product_id}&siteId=MLB&isItem=true&offset={offset}&limit={limit}&x-is-webview=false"

        request = requests.get(reviews_url, headers=headers)
        soup = BeautifulSoup(request.content, 'html.parser')

        if request.status_code != 200:
            print(f"Erro na requisição({request.status_code}):{request.text}")
            break

        if soup.get_text() != None:
            review_elements = json.loads(soup.get_text())['reviews']
        else:
            print("Resposta vazia do servidor")

        if len(review_elements) == 0:
            print("Não há mais comentários para carregar.")
            df = pd.DataFrame(reviews_list)
            df['product_name'] = title
            df.to_csv('data/reviews.csv', index=False, sep='█')
            break

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

    return 'data/reviews.csv'



if __name__ == "__main__":
    product_id='MLB-1951114616'
    scrape_reviews(product_id=product_id)

# headers = {
#     'accept': 'application/json, text/plain, */*',
#     'accept-encoding': 'gzip, deflate, br, zstd',
#     'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
#     'cache-control': 'no-cache',
#     'cookie': '_d2id=9e348d92-101d-4900-8ab4-8bc56633cc0f; __gads=ID=88537c994fc6e179:T=1750250827:RT=1750250827:S=ALNI_MZG31IJOLWzTbBebDuUuVQcZ0lMfg; __gpi=UID=000010283a1e4f3b:T=1750250827:RT=1750250827:S=ALNI_MaaEfHVBdoAU0QL77OXBgvpp1FvFA; __eoi=ID=9e37a21329d1ee0c:T=1750250827:RT=1750250827:S=AA-AfjbUOWQ_bKtlrJs5Vl6H4A1V; orguserid=dZHd70hh4007; orguseridp=238779118; orgnickp=BIANCAMAYOR; ssid=ghy-062210-B3rnBFWkWTObxTsxXyEZsiSlANOB0Z-__-238779118-__-1845296425538--RRR_0-RRR_0; ftid=OxiaI60dlcKXJwVVYAkZEEW8cgwOr8kL-1719229496502; cookiesPreferencesNotLogged=%7B%22categories%22%3A%7B%22advertising%22%3Atrue%2C%22functionality%22%3Anull%2C%22performance%22%3Anull%2C%22traceability%22%3Anull%7D%7D; _ga=GA1.1.778609086.1750248488; _ga_NDJFKMJ2PD=GS2.1.s1751547060$o34$g1$t1751548525$j60$l0$h0; _gcl_au=1.1.1612443903.1758546212; QSI_SI_5j6Ek3IHl7l6UTA_intercept=true; c_ui-navigation=6.6.150; c_pdp=1.158.0; _uetvid=75f1927050f211f0849ff1d183398249; _csrf=RtEE3By0pxqxn_wS60jdSWIG; cookiesPreferencesLoggedFallback=%7B%22userId%22%3A238779118%2C%22categories%22%3A%7B%22advertising%22%3Atrue%2C%22functionality%22%3Anull%2C%22performance%22%3Anull%2C%22traceability%22%3Anull%7D%7D; _mldataSessionId=f7dd9c04-504f-42d4-8ad1-78522f1612af; cookiesPreferencesLogged=%7B%22userId%22%3A238779118%2C%22categories%22%3A%7B%22advertising%22%3Atrue%2C%22functionality%22%3Anull%2C%22performance%22%3Anull%2C%22traceability%22%3Anull%7D%7D; hide-cookie-banner=238779118-COOKIE_PREFERENCES_ALREADY_SET; nsa_rotok=eyJhbGciOiJSUzI1NiIsImtpZCI6IjMiLCJ0eXAiOiJKV1QifQ.eyJpZGVudGlmaWVyIjoiNmU2Yjg3ZmUtYzU2NS00M2NjLWI4OWQtYmM4Yzg2Nzc1ZTQ1Iiwicm90YXRpb25faWQiOiI2M2ViNTgyNC0yM2UzLTQyOTMtOTMyMC1mYjc3OTVhNzgwY2MiLCJwbGF0Zm9ybSI6Ik1MIiwicm90YXRpb25fZGF0ZSI6MTc2MTUwNzA1OSwiZXhwIjoxNzY0MDk4NDU5LCJqdGkiOiI5NzIzZDk5MC0zZmJjLTRmNDQtYjNiMy1mNmE5YTE2MjAwMDgiLCJpYXQiOjE3NjE1MDY0NTksInN1YiI6IjZlNmI4N2ZlLWM1NjUtNDNjYy1iODlkLWJjOGM4Njc3NWU0NSJ9.Xa8TfeSDJWT6bfrZnC6Eq0BPzECDKjjiTuT2ANfD1Pzj2KWA0Sg2WyHLs6THl-Dy5S80_w15n06nWTbB1ZvPdTZijJUyXceVD6kafktE1iHCRQiijdCgX7H0iuTjK4Mi07K_lpYEtF-iZI199zT5LPSn9yFwXuncwyn0fpixFFX2bXm8uFJXcObwmWDwpl9xwwmXIJ285h8EYmYJ0sxFdXcjWCRpASDlsc8vPnKf2rZCIfQYIec73Yj1Eyky8z2duk8rhJ3ZdwHc585cd45oRkTue_ysYCL0DPhulzl6IvtOvmnqbru8e6EZTfwdZnXTRW3SEdzuJEKztzGfQ5TupA',
#     # 'csrf-token': 'NL3FDgT1-ae8HX29j5yOgdvFdscT7cci_S_c', # Pode ser redundante se x-csrf-token for usado
#     'd2id': '9e348d92-101d-4900-8ab4-8bc56633cc0f',
#     'device': 'desktop',
#     'device-memory': '8',
#     'downlink': '3.95',
#     'dpr': '0.9',
#     'ect': '4g',
#     # 'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6Ijk4OTU4NiIsImFwIjoiMTgzNDgzODM1OCIsImlkIjoiYmI5MzAxYmI2MjEzNzhhOCIsInRyIjoiOWQ1OGIxZTQ0MmU1NjFlZGUxYWVhYmM5ZmQzZmI4MGEiLCJ0aSI6MTc2MTUwNjQ2NDg3OCwidGsiOiIxNzA5NzA3In19', # Geralmente não necessário
#     'pragma': 'no-cache',
#     'priority': 'u=1, i',
#     'referer': 'https://produto.mercadolivre.com.br/noindex/catalog/reviews/MLB1951114616',
#     'rtt': '150',
#     'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Opera GX";v="122"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
#     'sec-fetch-dest': 'empty',
#     'sec-fetch-mode': 'cors',
#     'sec-fetch-site': 'same-origin',
#     # 'traceparent': '00-9d58b1e442e561ede1aeabc9fd3fb80a-bb9301bb621378a8-01', # Geralmente não necessário
#     # 'tracestate': '1709707@nr=0-1-989586-1834838358-bb9301bb621378a8----1761506464878', # Geralmente não necessário
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 OPR/122.0.0.0',
#     'viewport-width': '1128',
#     # 'withcredentials': 'true', # requests lida com cookies automaticamente, isso não é um header padrão
#     'x-client-name': 'desktop',
#     'x-client-version': '0.5',
#     'x-csrf-token': 'NL3FDgT1-ae8HX29j5yOgdvFdscT7cci_S_c',
#     'x-is-webview': 'false', # Já está nos params, talvez não precise aqui também
#     'x-meli-trace-site': 'MLB',
#     # 'x-newrelic-id': 'XQ4OVF5VGwIGXVhXAwAEUlA=', # Geralmente não necessário
#     'x-requested-with': 'XMLHttpRequest',
#     'x-user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 OPR/122.0.0.0',
# }
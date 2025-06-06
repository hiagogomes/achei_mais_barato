# apis/shopee.py

import json
import time
import hashlib
import requests
from django.conf import settings

APP_ID = settings.SHOPEE_APP_ID
SECRET = settings.SHOPEE_SECRET
API_URL = 'https://open-api.affiliate.shopee.com.br/graphql'

palavras_irrelevantes = {"do", "da", "de", "dos", "das", "a", "o", "e", "com", "para", "no", "na", "em"}


def limpar_termo_buscado(termo):
    palavras = termo.lower().split()
    return " ".join([p for p in palavras if p not in palavras_irrelevantes])


def buscar_produtos_shopee(termo, limite=50):
    termo_limpo = limpar_termo_buscado(termo)
    resultados = []

    payload_dict = {
        "query": """
            query Fetch($limit:Int, $keyword:String){
                productOfferV2(
                    listType: 0,
                    sortType: 2,
                    page: 1,
                    limit: $limit,
                    keyword: $keyword
                ) {
                    nodes {
                        productName
                        price
                        commission
                        productLink
                        offerLink
                        imageUrl
                    }
                }
            }
        """,
        "operationName": "Fetch",
        "variables": {
            "limit": limite,
            "keyword": termo_limpo
        }
    }

    payload_str = json.dumps(payload_dict, separators=(',', ':'))

    timestamp = int(time.time())
    assinatura = hashlib.sha256((APP_ID + str(timestamp) + payload_str + SECRET).encode('utf-8')).hexdigest()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'SHA256 Credential={APP_ID},Timestamp={timestamp},Signature={assinatura}'
    }

    try:
        response = requests.post(API_URL, headers=headers, data=payload_str)
        data = response.json()
        produtos = data.get("data", {}).get("productOfferV2", {}).get("nodes", [])

        for item in produtos:
            resultados.append({
                "nome": item.get("productName"),
                "preco": item.get("price"),
                "imagem": item.get("imageUrl"),
                "link": item.get("offerLink") or item.get("productLink"),
            })

    except Exception as e:
        print("Erro na API Shopee:", e)

    return resultados

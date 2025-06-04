import json
import os
import time
import hashlib
import logging
import requests
from django.shortcuts import render
from django.conf import settings

from .tasks import tarefa_demorada

# Logger configurado para registrar erros
logger = logging.getLogger(__name__)

# Variáveis sensíveis
APP_ID = settings.SHOPEE_APP_ID
SECRET = settings.SHOPEE_SECRET
API_URL = 'https://open-api.affiliate.shopee.com.br/graphql'
JSON_PATH = os.path.join(settings.BASE_DIR, 'website_amb', 'links.json')

# Palavras irrelevantes para limpar o termo
palavras_irrelevantes = {"do", "da", "de", "dos", "das", "a", "o", "e", "com", "para", "no", "na", "em"}

def minha_view(request):
    tarefa_demorada.delay()  # chama a task assincronamente
    return render(request, 'website_amb/index.html')

def gerar_headers(payload_str):
    """Gera headers com assinatura SHA256 exigidos pela API Shopee."""
    timestamp = int(time.time())
    fator = APP_ID + str(timestamp) + payload_str + SECRET
    assinatura = hashlib.sha256(fator.encode('utf-8')).hexdigest()

    return {
        'Content-Type': 'application/json',
        'Authorization': f'SHA256 Credential={APP_ID},Timestamp={timestamp},Signature={assinatura}'
    }


def limpar_termo_buscado(termo):
    """Remove palavras irrelevantes do termo de busca."""
    palavras = termo.lower().split()
    return " ".join([p for p in palavras if p not in palavras_irrelevantes])


def index(request):
    """View da página inicial."""
    return render(request, 'website_amb/index.html')


def resultado(request):
    """View que faz a busca na API Shopee e exibe os produtos."""
    termo_original = request.GET.get("q", "").strip().lower()
    termo = limpar_termo_buscado(termo_original)
    resultados = []

    if not termo:
        return render(request, "website_amb/resultado.html", {"produtos": []})

    page = 1
    payload_dict = {
        "query": """
            query Fetch($page:Int, $keyword:String){
                productOfferV2(
                    listType: 0,
                    sortType: 2,
                    page: $page,
                    limit: 50,
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
            "page": page,
            "keyword": termo
        }
    }

    payload_str = json.dumps(payload_dict, separators=(',', ':'))
    headers = gerar_headers(payload_str)

    try:
        response = requests.post(API_URL, headers=headers, data=payload_str)

        if response.status_code != 200:
            logger.error("Erro na API Shopee - Status code: %s", response.status_code)
            return render(request, "website_amb/resultado.html", {"produtos": []})

        data = response.json()
        produtos = data.get("data", {}).get("productOfferV2", {}).get("nodes", [])

        nomes_unicos = set()
        for item in produtos:
            nome = item.get("productName")
            if nome in nomes_unicos:
                continue
            nomes_unicos.add(nome)

            preco_raw = item.get("price", 0)
            try:
                preco_final = float(preco_raw) / 100 if isinstance(preco_raw, (int, float)) else 0.0
            except:
                preco_final = 0.0

            resultados.append({
                "nome": nome,
                "preco": preco_final,
                "imagem": item.get("imageUrl"),
                "link": item.get("offerLink") or item.get("productLink"),
            })

    except Exception as e:
        logger.exception("Erro ao buscar produtos na API Shopee")

    return render(request, "website_amb/resultado.html", {"produtos": resultados})

import json
import os
import time
import hashlib
import requests
from django.shortcuts import render
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Obtém as variáveis sensíveis do arquivo de configurações
APP_ID = settings.SHOPEE_APP_ID  # ID do aplicativo registrado na API da Shopee
SECRET = settings.SHOPEE_SECRET  # Chave secreta fornecida pela Shopee
API_URL = 'https://open-api.affiliate.shopee.com.br/graphql'  # URL da API GraphQL

# Caminho para o arquivo local onde links afiliados podem ser salvos
JSON_PATH = os.path.join(settings.BASE_DIR, 'website_amb', 'links.json')


def gerar_headers(payload_str):
    """
    Gera os headers exigidos pela API da Shopee, com assinatura baseada em hash SHA256.
    
    Parâmetros:
        payload_str (str): JSON da requisição em formato string.
    
    Retorna:
        dict: Headers prontos para envio à API.
    """
    timestamp = int(time.time())
    fator = APP_ID + str(timestamp) + payload_str + SECRET
    assinatura = hashlib.sha256(fator.encode('utf-8')).hexdigest()

    return {
        'Content-Type': 'application/json',
        'Authorization': f'SHA256 Credential={APP_ID},Timestamp={timestamp},Signature={assinatura}'
    }


def index(request):
    """
    View da página inicial. Renderiza o template com o formulário de busca.
    
    Parâmetros:
        request (HttpRequest): Requisição HTTP recebida.
    
    Retorna:
        HttpResponse: Página HTML com o campo de busca.
    """
    return render(request, 'website_amb/index.html')


# Palavras comuns que serão removidas do termo de busca para melhorar os resultados
palavras_irrelevantes = {"do", "da", "de", "dos", "das", "a", "o", "e", "com", "para", "no", "na", "em"}


def limpar_termo_buscado(termo):
    """
    Remove palavras irrelevantes do termo de busca para melhorar os resultados na API.

    Exemplo:
        Entrada: "camisa do cruzeiro"
        Saída: "camisa cruzeiro"

    Parâmetros:
        termo (str): Termo digitado pelo usuário.

    Retorna:
        str: Termo limpo.
    """
    palavras = termo.lower().split()
    return " ".join([p for p in palavras if p not in palavras_irrelevantes])


def resultado(request):
    """
    View da página de resultados.
    Faz a busca na API da Shopee com o termo digitado, limpa o termo se necessário,
    envia a requisição e processa os produtos retornados, com paginação.
    """
    # Termo original digitado pelo usuário
    termo_original = request.GET.get("q", "").strip().lower()
    
    # Remove palavras desnecessárias para melhorar os resultados
    termo = limpar_termo_buscado(termo_original)
    
    # Lista que armazenará os produtos encontrados
    resultados = []

    # Se nenhum termo válido foi digitado, retorna a página vazia
    if not termo:
        return render(request, "website_amb/resultado.html", {"produtos": []})

    # Página inicial da API (sempre começa em 1 para pegar os primeiros 50 produtos)
    page_api = 1

    # Estrutura do payload da requisição GraphQL
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
            "page": page_api,
            "keyword": termo
        }
    }

    # Transforma o dicionário em string compactada (sem espaços extras)
    payload_str = json.dumps(payload_dict, separators=(',', ':'))

    # Gera timestamp e assinatura para autenticação da requisição
    timestamp = int(time.time())
    fator = APP_ID + str(timestamp) + payload_str + SECRET
    assinatura = hashlib.sha256(fator.encode('utf-8')).hexdigest()

    # Headers com autenticação
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'SHA256 Credential={APP_ID},Timestamp={timestamp},Signature={assinatura}'
    }

    try:
        # Envia requisição POST à API
        response = requests.post(API_URL, headers=headers, data=payload_str)
        data = response.json()

        # Extrai a lista de produtos da resposta
        produtos = data.get("data", {}).get("productOfferV2", {}).get("nodes", [])

        # Constrói lista de dicionários com dados simplificados
        for item in produtos:
            resultados.append({
                "nome": item.get("productName"),
                "preco": item.get("price"),
                "imagem": item.get("imageUrl"),
                "link": item.get("offerLink") or item.get("productLink"),
            })

    except Exception as e:
        print("Erro ao buscar produtos:", e)

    # Paginação no Django para a lista de resultados (20 produtos por página)
    itens_por_pagina = 20
    paginator = Paginator(resultados, itens_por_pagina)

    # Página atual da URL GET (parâmetro "pagina")
    pagina = request.GET.get('pagina', 1)

    try:
        produtos_paginados = paginator.page(pagina)
    except PageNotAnInteger:
        produtos_paginados = paginator.page(1)
    except EmptyPage:
        produtos_paginados = paginator.page(paginator.num_pages)

    contexto = {
        "produtos": produtos_paginados,
        "pagina": produtos_paginados.number,
        "tem_anterior": produtos_paginados.has_previous(),
        "tem_proxima": produtos_paginados.has_next(),
        "termo": termo_original,
    }

    return render(request, "website_amb/resultado.html", contexto)

def sobre(request):
    return render(request, 'website_amb/sobre.html')

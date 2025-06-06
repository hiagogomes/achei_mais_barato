from django.shortcuts import render
from django.core.paginator import Paginator
from apis.shopee import buscar_produtos_shopee
from website_amb.utils.pesquisa_logger import registrar_termo
from datetime import datetime

def index(request):
    return render(request, 'website_amb/index.html')

def termos(request):
    return render(request, 'website_amb/termos.html', {'data': datetime.now()})

def politica_afiliados(request):
    return render(request, 'website_amb/politica_afiliados.html', {'data': datetime.now()})

def politica_privacidade(request):
    return render(request, 'website_amb/politica_privacidade.html', {'data': datetime.now()})

def sobre(request):
    return render(request, 'website_amb/sobre.html')

def contato(request):
    return render(request, 'website_amb/contato.html')

def resultado(request):
    termo = request.GET.get("q", "").strip()
    pagina = int(request.GET.get("pagina", 1))
    produtos = []

    if termo:

        try:
            # Buscar produtos apenas da Shopee (por enquanto)
            produtos_shopee = buscar_produtos_shopee(termo, limite=50)

            # Adiciona tag de origem para futura expansão
            for p in produtos_shopee:
                p["origem"] = "Shopee"

            # Lista de produtos atual (futuramente incluir outras fontes)
            produtos = produtos_shopee

            # Ordenar por preço
            produtos.sort(key=lambda x: x["preco"])

        except Exception as e:
            print("Erro na busca de produtos:", e)

        # Registrar termo e se encontrou produto ou não
        encontrou = len(produtos) > 0
        registrar_termo(termo, encontrou)

    # Paginação (20 produtos por página)
    paginador = Paginator(produtos, 20)
    pagina_obj = paginador.get_page(pagina)

    return render(request, "website_amb/resultado.html", {
        "termo": termo,
        "pagina": pagina,
        "tem_anterior": pagina_obj.has_previous(),
        "tem_proxima": pagina_obj.has_next(),
        "produtos": pagina_obj.object_list,
    })

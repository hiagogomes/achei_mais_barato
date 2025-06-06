# website_amb/utils/pesquisa_logger.py
import json
import os
from datetime import datetime

CAMINHO_JSON = os.path.join(os.path.dirname(__file__), 'termos_pesquisados.json')

def carregar_dados():
    if not os.path.exists(CAMINHO_JSON):
        return []
    with open(CAMINHO_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_dados(dados):
    with open(CAMINHO_JSON, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def registrar_termo(termo, encontrou_produto):
    hoje = datetime.now().strftime('%Y-%m-%d')
    dados = carregar_dados()

    # Procurar registro do termo na mesma data
    for registro in dados:
        if registro['termo'].lower() == termo.lower() and registro['data'] == hoje:
            registro['quantidade'] += 1
            # Atualizar status "encontrou_produto" se ainda não estiver True e o novo resultado for True
            if encontrou_produto and not registro.get('encontrou_produto', False):
                registro['encontrou_produto'] = True
            salvar_dados(dados)
            return

    # Se não achou, cria novo registro
    dados.append({
        'termo': termo,
        'data': hoje,
        'quantidade': 1,
        'encontrou_produto': bool(encontrou_produto)
    })
    salvar_dados(dados)

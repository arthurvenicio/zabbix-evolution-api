#!/usr/bin/env python3
#
# 

import os
import sys
import subprocess

# Função para verificar e instalar dependências
def check_dependencies():
    try:
        import requests
    except ImportError:
        print("A biblioteca 'requests' não está instalada. Instalando agora...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests

# Verifica dependências antes de continuar
check_dependencies()

import requests
import base64

# Função para forçar o usuário a passar os parâmetros necessários
def check_arguments():
    expected_args = 10
    if len(sys.argv) != expected_args:
        print(f"Erro: Número incorreto de argumentos fornecidos.")
        print(f"Usage: {sys.argv[0]} {{URLZBX}} {{TOKENZBX}} {{ITEMIDZBX}} {{URLAPI}} {{APIKEY}} {{INSTANCE}} {{TO}} {{SUBJECT}} {{MSG}}\n")
        print(f"Example:\n{'='*8}")
        print(f"{sys.argv[0]} https://zabbix.seudominio.com KHKHKHGKGJ 48061 https://api.seudominio.com KHKHKHGKGJ Teste 550000000000 'Subject' 'Msg from to WhatsApp'")
        print(f"\n")
        sys.exit(1)

    url_zbx = sys.argv[1]
    token_zbx = sys.argv[2]
    item_id_zbx = sys.argv[3]
    url_api = sys.argv[4]
    token = sys.argv[5]
    instance = sys.argv[6]
    to = sys.argv[7]
    subject = sys.argv[8]
    msg = sys.argv[9]

    if not url_zbx.startswith("http://") and not url_zbx.startswith("https://"):
        print("Erro: URLZBX deve começar com 'http://' ou 'https://'.")
        sys.exit(1)
    if not token_zbx:
        print("Erro: USERZBX não pode estar vazio.")
        sys.exit(1)
    if not item_id_zbx.isdigit():
        print("Erro: ITEMIDZBX deve ser um número.")
        sys.exit(1)
    if not url_api.startswith("http://") and not url_api.startswith("https://"):
        print("Erro: URLAPI deve começar com 'http://' ou 'https://'.")
        sys.exit(1)
    if not token:
        print("Erro: APIKEY não pode estar vazio.")
        sys.exit(1)
    if not instance:
        print("Erro: INSTANCE não pode estar vazio.")
        sys.exit(1)
    if not to.isdigit():
        print("Erro: TO deve ser um número.")
        sys.exit(1)
    if not subject:
        print("Erro: SUBJECT não pode estar vazio.")
        sys.exit(1)
    if not msg:
        print("Erro: MSG não pode estar vazio.")
        sys.exit(1)

# Função principal
def main():
    check_arguments()

    # Parâmetros extras para o gráfico
    _from = "now-6h"               						# Tempo inicial
    _to = "now"                    						# Tempo final
    _with = "1024"                 						# Largura do gráfico
    _height = "220"                						# Altura do gráfico
    _type = "0"                    						# 0=linha simples, 1=empilhado quando há mais de um parâmetro no mesmo gráfico
    _profileIdx = "web.item.graph.filter" 		# Função do gráfico

    # Leitura dos parâmetros obrigatórios
    _ZABBIX_BASE = sys.argv[1]                # URLZBX: URL base do Zabbix
    _ZABBIX_COOKIE = sys.argv[2]                # USERXBX: usuário com permissão de leitura
    _ZABBIX_ITEM_ID = sys.argv[3]             # ITEMID: Ex: 48061 - Utilização de CPU do Zabbix Server (%)
    _WA_API_URL = sys.argv[4]                  # URLAPI: API do WhatsApp para enviar imagens
    _WA_APIKEY = sys.argv[5]                  # Token da API
    _WA_INSTANCE = sys.argv[6]                # Instancia da API
    _WA_TO = sys.argv[7]                      # Destinatário do WhatsApp
    _WA_SUBJECT = sys.argv[8]                 # Assunto
    _WA_MSG = sys.argv[9]                    # Mensagem a ser enviada no WhatsApp

    # Sessão do requests
    session = requests.Session()
        
    session.headers.update({
        'Cookie': 'zbx_session=' + _ZABBIX_COOKIE
    })

    # URL do gráfico específico
    graph_url = f'{_ZABBIX_BASE}/chart.php?from={_from}&to={_to}&itemids[0]={_ZABBIX_ITEM_ID}&type={_type}&profileIdx={_profileIdx}&width={_with}&height={_height}'

    # Faz a requisição do gráfico
    graph_response = session.get(graph_url, verify=False)

    # Verifica se a requisição foi bem-sucedida
    if graph_response.status_code != 200:
        print('Falha ao obter o gráfico')
        sys.exit(1)

    # Codifica a imagem em base64 diretamente da resposta
    base64_image = base64.b64encode(graph_response.content).decode('utf-8')

    # Prepara a mensagem para enviar via WhatsApp API
    wa_msg = f"{_WA_SUBJECT}\n{_WA_MSG}"

    # Envia a imagem via WhatsApp API
    wa_send_url = f'{_WA_API_URL}/message/sendMedia/{_WA_INSTANCE}'
    data = {
				"number": _WA_TO,
				"mediatype": "image",
				"mimetype": "image/png",
				"caption": wa_msg,
    		    "media": base64_image,
				"fileName": "chart.png",
				"delay": 1200
		}
    
    headers = {
        'Content-Type': 'application/json',
        'apikey': _WA_APIKEY
    }

    response = requests.post(wa_send_url, json=data, headers=headers, verify=False)

    # Verifica se o envio foi bem-sucedido
    if response.status_code == 201:
        print('Mensagem e gráfico enviados com sucesso')
    else:
        print('Falha ao enviar mensagem e gráfico')

# Executa a função principal
if __name__ == "__main__":
    main()
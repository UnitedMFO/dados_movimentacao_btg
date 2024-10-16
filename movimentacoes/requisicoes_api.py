import requests
import os
from dotenv import load_dotenv
from UUID import gerador_uuid

# Carregar as variáveis de ambiente
load_dotenv()

# Constantes de URL e autenticação
URL_API_TOKEN = os.getenv('API_URL_TOKEN')
CREDENCIAIS_BASIC_AUTH = os.getenv('BASIC_AUTH')
PARTNER_REQUEST_ID = os.getenv('PARTNER_REQUEST_ID_TOKEN')
URL_API_MOVIMENTACOES = os.getenv('API_MOVEMENT_URL')
URL_API_DADOS_CLIENTE = os.getenv('API_URL_DADOS')


def obter_token_autenticacao():
    """Obtém o token de autenticação para requisições"""
    url = URL_API_TOKEN
    headers = {
        "Authorization": f"Basic {CREDENCIAIS_BASIC_AUTH}",
        "x-id-partner-request": gerador_uuid(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    body = {
        "grant_type": "client_credentials"
    }

    try:
        response = requests.post(url, headers=headers, data=body)
        response.raise_for_status()

        # Extrair o token dos cabeçalhos da resposta
        token_autenticacao = response.headers.get('access_token')
        return token_autenticacao

    except requests.exceptions.HTTPError as http_error:
        print(f"Erro HTTP: {http_error}")
    except Exception as e:
        print(f"Erro ao obter o token de autenticação: {e}")
    return None


def fazer_requisicao_movimentacoes(codigo_cliente, data_inicio, data_fim, token_autenticacao):
    """Faz requisição para obter movimentações de um cliente em um período especificado"""
    url = f"{URL_API_MOVIMENTACOES}{codigo_cliente}"
    headers = {
        "x-id-partner-request": gerador_uuid(),
        "access_token": token_autenticacao
    }
    body = {
        "startDate": data_inicio,
        "endDate": data_fim
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        print("Requisição de movimentações concluída com sucesso.")
    except requests.exceptions.HTTPError as http_error:
        print(f"Erro HTTP ao fazer a requisição de movimentações: {http_error}")
    except Exception as e:
        print(f"Erro ao fazer a requisição de movimentações: {e}")


def obter_dados_cadastrais_cliente(codigo_cliente, token_autenticacao):
    """Obtém os dados cadastrais de um cliente utilizando o código de cliente"""
    url = URL_API_DADOS_CLIENTE.replace("{account_number}", codigo_cliente)
    headers = {
        "x-id-partner-request": gerador_uuid(),
        "access_token": token_autenticacao
    }

    try:
        resposta = requests.get(url, headers=headers)

        if resposta.status_code == 200:
            return resposta.json()
        elif resposta.status_code == 401:
            print("Código do cliente inválido. Tente novamente.")
            return None
    except Exception as e:
        print(f"Erro ao obter os dados cadastrais do cliente: {e}")
    return None

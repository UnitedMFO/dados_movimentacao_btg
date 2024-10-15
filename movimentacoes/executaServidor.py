from flask import Flask, request
import os
import requests
from zipfile import ZipFile
from threading import Event

app = Flask(__name__)

def run_server():
    app.run(port=5000)

# Criando um evento de threading para sinalizar quando o webhook terminar
webhook_completed_event = Event()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    print("Encerrando o servidor...")
    os._exit(0)  # Encerra o processo do Python

@app.route('/hello', methods=['GET'])
def hello():
    return 'Hello, world!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    # Extrai accountNumber e URL do arquivo ZIP
    account_number = data.get('response', {}).get('accountNumber', 'unknown')
    file_url = data.get('response', {}).get('url')

    # Verifica se o file_url foi fornecido
    if not file_url:
        print("Erro: URL do arquivo não foi fornecida ou está nula.")
        return {'error': 'URL do arquivo não foi fornecida'}, 400  # Retorna um código 400 Bad Request

    try:
        # Definir o nome do arquivo ZIP com base no accountNumber
        zip_filename = f'{account_number}.zip'

        # Fazer o download do arquivo ZIP
        response = requests.get(file_url)
        if response.status_code == 200:
            # Salvar o arquivo ZIP
            with open(zip_filename, 'wb') as zip_file:
                zip_file.write(response.content)
            print(f'Arquivo {zip_filename} baixado com sucesso.')

            # Extrair o conteúdo do arquivo ZIP na pasta atual
            with ZipFile(zip_filename, 'r') as zip_ref:
                zip_ref.extractall()
            print(f'Arquivo {zip_filename} extraído com sucesso.')

            # Renomear o arquivo extraído para o accountNumber
            extracted_files = zip_ref.namelist()
            if extracted_files:
                original_name = extracted_files[0]  # Assume que há apenas um arquivo extraído
                new_name = f'{account_number}{os.path.splitext(original_name)[1]}'
                os.rename(original_name, new_name)
                print(f'Arquivo {original_name} renomeado para {new_name}.')

            # Remover o arquivo ZIP após a extração
            os.remove(zip_filename)
        else:
            print(f'Falha ao baixar o arquivo: {response.status_code}')
            return {'error': f'Falha ao baixar o arquivo, status code: {response.status_code}'}, 500

    except Exception as e:
        print(f"Erro no processamento do arquivo: {e}")
        return {'error': 'Erro no processamento do arquivo'}, 500

    # Sinaliza que o processamento do webhook foi concluído
    webhook_completed_event.set()

    print("Requisição recebida com sucesso.")
    return 'OK', 200

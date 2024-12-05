import threading
import requests
import time
import sys
import os
from executaServidor import run_server, webhook_completed_event
from requisicoes_api import obter_token_autenticacao, fazer_requisicao_movimentacoes
from trate_data_csv import criar_relatorio_movimentacoes, formatar_relatorio_movimentacoes, calcular_valor_liquido, \
    destacar_valores_negativos, criar_planilha_resumo
from base_clientes import ler_lista_clientes


def listar_arquivos_xlsx():
    # Obtém o diretório onde o script está localizado
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))

    # Cria uma lista para armazenar os nomes dos arquivos .xlsx
    lista_nomes_xlsx = []

    # Percorre todos os arquivos no diretório do script
    for arquivo in os.listdir(diretorio_atual):
        # Verifica se o arquivo tem extensão .xlsx
        if arquivo.endswith('.csv'):
            # Adiciona apenas o nome do arquivo à lista
            lista_nomes_xlsx.append(arquivo)

    return lista_nomes_xlsx


def encontrar_correspondencia(codigo, lista_clientes):
    # Separar as duas listas dentro de nome_arquivo
    codigo_clientes, titular = lista_clientes

    # Verifica se o código está na primeira lista (lista_1)
    if codigo in codigo_clientes:
        # Pega o índice do código em lista_1
        index = codigo_clientes.index(codigo)
        # Retorna o valor correspondente da segunda lista (lista_2)
        return titular[index]

    # Retorna None se o código não for encontrado
    return None

def processar_relatorio_final():
    arquivos_csv = listar_arquivos_xlsx()
    lista_clientes = ler_lista_clientes()
    try:
        for arquivo in arquivos_csv:
            # Remove a extensão do arquivo e tenta encontrar correspondência
            codigo = arquivo.replace(".csv", "")
            titular = encontrar_correspondencia(codigo, lista_clientes)

            # Verifica se encontrou correspondência antes de continuar
            if titular is None:
                print(f"Não foi possível encontrar um cliente correspondente para o arquivo: {arquivo}")
                continue  # Pula para o próximo arquivo

            titular += "_EM"  # Concatena apenas se titular for válido
            print(titular, arquivo)

            excel_filename = criar_relatorio_movimentacoes(arquivo, titular)
            formatar_relatorio_movimentacoes(excel_filename)
            calcular_valor_liquido(excel_filename)
            destacar_valores_negativos(excel_filename)
            criar_planilha_resumo(excel_filename)
            print(f"Relatório finalizado com sucesso: {excel_filename}")
            print("\n")
    except Exception as e:
        print(f"Erro ao processar o relatório: {e}")


processar_relatorio_final()


def iniciar_servidor():
    # Inicia o servidor Flask
    try:
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        print("Servidor Flask iniciado.")
        time.sleep(2)  # Pausa para garantir que o servidor está rodando
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")
        sys.exit(1)


def fecha_servidor():
    # Encerra o servidor Flask após o processamento de todos os clientes
    try:
        response = requests.post('http://127.0.0.1:5000/shutdown')
        if response.status_code == 200:
            print("Servidor encerrado com sucesso.")
        else:
            print(f"Falha ao encerrar o servidor: {response.status_code}")
            print(response.text)
    except Exception as shutdown_error:
        print(f"Erro ao tentar encerrar o servidor: {shutdown_error}")
    sys.exit(0)


def percorrer_codigo_clientes(codigo_clientes, token, data_req):
    for codigo_cliente in codigo_clientes:
        print("\n")
        print(f"Processando cliente {codigo_cliente}...")
        try:
            fazer_requisicao_movimentacoes(codigo_cliente, data_req[0], data_req[1], token)
        except Exception as e:
            print(f"Erro ao executar a requisição de movimento para o cliente {codigo_cliente}: {e}")
            continue
        print("Aguardando o término do processamento do webhook (até 5 minutos)...")

        if webhook_completed_event.wait(timeout=300):  # Espera até 300 segundos (5 minutos)
            print("Webhook processado com sucesso.")
            webhook_completed_event.clear()
        else:
            print(
                f"Tempo limite de 5 minutos atingido para o cliente {codigo_cliente}. Pulando para o próximo cliente.")


def main():
    codigos_clientes = ler_lista_clientes()

    iniciar_servidor()

    # Obtém o token de autenticação e a data de requisição uma vez
    try:
        token = obter_token_autenticacao()
        data_req = ["2024-11-01", "2024-11-30"]
    except Exception as e:
        print(f"Erro ao obter o token de autenticação ou data: {e}")
        sys.exit(1)

    percorrer_codigo_clientes(codigos_clientes, token, data_req)

    fecha_servidor()

#
# if __name__ == '__main__':
#     main()

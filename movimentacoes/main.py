import threading
import requests
import time
import sys
from executaServidor import run_server, webhook_completed_event  # Importa o evento do servidor
from validacao_de_dados import obter_codigo_cliente, obter_data_post
from requisicoes_api import obter_token_autenticacao, fazer_requisicao_movimentacoes
from trate_data_csv import criar_relatorio_movimentacoes, formatar_relatorio_movimentacoes, calcular_valor_liquido, destacar_valores_negativos, criar_planilha_resumo

def main():
    # Inicia o servidor Flask uma vez no início
    try:
        server_thread = threading.Thread(target=run_server, daemon=True)  # Daemon para fechar automaticamente no final
        server_thread.start()
        print("Servidor Flask iniciado.")
        time.sleep(2)  # Pausa para garantir que o servidor está rodando
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")
        sys.exit(1)

    while True:
        # Solicitar credenciais do cliente
        try:
            token = obter_token_autenticacao()
            data_req = obter_data_post()
            codigo_cliente, base_nome_arquivo = obter_codigo_cliente(token, data_req[0])
        except Exception as e:
            print(f"Erro ao obter as credenciais ou código do cliente: {e}")
            continue

        # Tentar fazer a requisição de movimentação
        try:
            fazer_requisicao_movimentacoes(codigo_cliente, data_req[0], data_req[1], token)
        except Exception as e:
            print(f"Erro ao executar a requisição de movimento: {e}")
            continue

        print("Aguardando o término do processamento do webhook...")

        # Espera indefinidamente até que o webhook seja completado
        webhook_completed_event.wait()  # Aguarda até o webhook ser sinalizado (sem limite de tempo)

        # Reseta o evento para o próximo loop
        webhook_completed_event.clear()

        # Processar o arquivo gerado após o webhook
        csv_filename = f'{codigo_cliente}.csv'
        try:
            excel_filename = criar_relatorio_movimentacoes(csv_filename, base_nome_arquivo)
            formatar_relatorio_movimentacoes(excel_filename)
            calcular_valor_liquido(excel_filename)
            destacar_valores_negativos(excel_filename)
            criar_planilha_resumo(excel_filename)
            print("Processamento concluído com sucesso.")
        except Exception as e:
            print(f"Erro ao processar o arquivo: {e}")
            continue

        # Pergunta ao usuário se deseja processar outro cliente
        resposta = input("Deseja processar outro cliente? (1 - Sim, 0 - Não): ")
        if resposta != '1':
            break  # Sai do loop se a resposta não for '1'

    # Encerra o servidor Flask quando o usuário decide sair
    try:
        response = requests.post('http://127.0.0.1:5000/shutdown')
        if response.status_code == 200:
            print("Servidor encerrado com sucesso.")
        else:
            print(f"Falha ao encerrar o servidor: {response.status_code}")
            print(response.text)
    except Exception as shutdown_error:
        print(f"Erro ao tentar encerrar o servidor: {shutdown_error}")

    print("Encerrando o programa.")
    sys.exit(0)

if __name__ == '__main__':
    main()

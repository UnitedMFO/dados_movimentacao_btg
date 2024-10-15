import os
import sys
from utils import validar_data
from api_requests import requisicao_dados_cadastrais
from datetime import date, timedelta


def obter_data_post():
    # Define o primeiro e o último dia do mês anterior
    endDate = (date.today().replace(day=1) - timedelta(days=1))
    startDate = endDate.replace(day=1)

    # Formata as datas como strings
    startDate = startDate.strftime('%Y-%m-%d')
    endDate = endDate.strftime('%Y-%m-%d')

    # Solicita ao usuário se deseja alterar as datas padrão
    if int(input(f"A data padrão do EXTRATO MENSAL é de ({startDate}) a ({endDate}) - Deseja alterar? (1 - Sim, 0 - Não): ")) == 1:
        while True:
            startDate = input("Digite a data INICIAL desejada (AAAA-MM-DD): ")
            endDate = input("Digite a data FINAL desejada (AAAA-MM-DD): ")
            if validar_data(startDate, endDate):
                return startDate, endDate
            print("Formato de data inválido, tente novamente.")

    return startDate, endDate


def obter_codigo_cliente(token,data):
    while True:
        codigo_cliente = input("Digite o código do cliente: ")

        if len(codigo_cliente) == 9 and codigo_cliente.isdigit():
            dados = requisicao_dados_cadastrais(codigo_cliente, token)

            # Se os dados forem válidos, retorna; caso contrário, informa o erro e repete o loop
            if dados is not None:
                nome_completo = dados.get('holder')['name'].split()
                data_atual = data.split('-')
                iniciais = ''
                for nome in nome_completo:
                    iniciais += nome[0]

                iniciais = iniciais + "_EM_" + data_atual[1] + "_" + data_atual[0]

                print(f"Cliente encontrado: {dados.get('holder')['name']}")

                return codigo_cliente,iniciais
            else:
                print("Código do cliente inválido. Tente novamente.")
        else:
            print("O Código do cliente deve ter 9 números. Tente novamente.")


import xlwings as xw
import pandas as pd
import os

def ler_lista_clientes():
    caminho_arquivo = os.path.join(os.path.dirname(__file__), '..', 'Base_Clientes.xlsx')

    # Carrega o arquivo Excel
    df = pd.read_excel(caminho_arquivo, sheet_name='ClientesBTG', header=1)

    # Corrige espaços extras nos nomes das colunas
    df.columns = df.columns.str.strip()

    # Converte explicitamente 'Código' para string para preservar zeros à esquerda
    df['Código'] = df['Código'].apply(lambda x: f"{x:09}")  # Assume que todos os códigos devem ter 8 dígitos

    # Extrai as colunas 'Código' e 'Cliente' como listas
    codigo_clientes = df['Código'].tolist()
    clientes = df['Titular'].tolist()

    # Retorna as listas de códigos e clientes
    return codigo_clientes,clientes






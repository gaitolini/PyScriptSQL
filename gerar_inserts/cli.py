# gerar_inserts/cli.py

import argparse
from gerar_inserts.core import gerar_comandos_insert, salvar_comandos

def main():
    parser = argparse.ArgumentParser(description="Gerador de scripts SQL INSERT.")
    parser.add_argument("arquivo_dados", help="Caminho para o arquivo de dados de entrada (ex: CSV).")
    parser.add_argument("-o", "--output", default="inserts.sql", help="Nome do arquivo de saída para os comandos SQL.")
    # No futuro, você pode adicionar mais argumentos aqui para outras funcionalidades

    args = parser.parse_args()

    try:
        # Aqui você precisará implementar a lógica para ler os dados do arquivo
        # args.arquivo_dados e transformá-los em uma estrutura que sua função
        # gerar_comandos_insert espera. Por exemplo, se for um CSV, você pode
        # usar a biblioteca csv do Python.
        with open(args.arquivo_dados, 'r') as f:
            linhas = [linha.strip().split(',') for linha in f] # Exemplo simples para CSV

        # Adapte a chamada de acordo com a estrutura dos seus dados
        dados_processados = []
        if linhas:
            cabecalho = linhas[0] # Se a primeira linha for o cabeçalho
            for linha in linhas[1:]:
                dados_processados.append(dict(zip(cabecalho, linha)))
            comandos = gerar_comandos_insert(dados_processados)
            salvar_comandos(comandos, args.output)
        else:
            print("Arquivo de dados vazio.")

    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado: {args.arquivo_dados}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()
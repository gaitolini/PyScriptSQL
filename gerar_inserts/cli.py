# gerar_inserts/cli.py

import sys
import os

# Adiciona o diretório pai (raiz do projeto) ao sys.path se não estiver lá
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.append(root_path)

from gerar_inserts.oracle_utils import obter_conexao, obter_sequencia
from gerar_inserts.script_generator import gerar_script_carga
from gerar_inserts.tabelas import gerar_script_inclusao_tabela
from gerar_inserts.campos import gerar_script_inclusao_campos, obter_informacoes_campos

def exibir_menu():
    print("\n--- Gerador de Scripts SQL ---")
    print("Escolha uma opção:")
    print("1 - SCIncDefault: Gerar INSERTS de carga de dados")
    print("2 - SCIncTabelas: Gerar INSERT para a tabela A_TABELAS")
    print("3 - SCIncCampos: Gerar INSERT para a tabela A_CAMPOS")
    print("0 - Sair e Fechar Conexão")
    return input("Digite o número da opção desejada: ")

def main():
    connection = obter_conexao()
    if not connection:
        print("Não foi possível estabelecer conexão. Encerrando.")
        return

    while True:
        opcao = exibir_menu()

        if opcao == '1':
            nome_responsavel = input("Digite o nome do responsável pela geração do script: ")
            query_usuario = input("Digite a query SELECT para extrair os dados: ")
            with connection.cursor() as cursor:
                usar_sequencia, sequence_name = obter_sequencia(cursor)
                gerar_script_carga(cursor, query_usuario, nome_responsavel, usar_sequencia, sequence_name)
        elif opcao == '2':
            with connection.cursor() as cursor:
                gerar_script_inclusao_tabela(cursor)
        elif opcao == '3':
            query_campos = obter_informacoes_campos(connection)
            with connection.cursor() as cursor:
                gerar_script_inclusao_campos(cursor, query_campos)
        elif opcao == '0':
            print("Fechando a conexão com o banco de dados e saindo.")
            connection.close()
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
# gerar_inserts/cli.py

from gerar_inserts.oracle_utils import obter_conexao, obter_sequencia
from gerar_inserts.script_generator import gerar_script_carga

def main():
    nome_responsavel_anterior = ""

    while True:
        connection = obter_conexao()
        if not connection:
            print("Não foi possível estabelecer conexão. Encerrando.")
            break

        nome_responsavel = input(f"Digite o nome do responsável pela geração do script (sugerido: {nome_responsavel_anterior}): ") or nome_responsavel_anterior
        query_usuario = input("Digite a query SELECT para extrair os dados (ex: SELECT * FROM sua_tabela WHERE ...): ")

        with connection.cursor() as cursor:
            usar_sequencia, sequence_name = obter_sequencia(cursor)

            if gerar_script_carga(cursor, query_usuario, nome_responsavel, usar_sequencia, sequence_name):
                nome_responsavel_anterior = nome_responsavel # Sugere o último nome usado

        connection.close()

        gerar_outro = input("Deseja gerar outro script SQL? (s/n): ").lower()
        if gerar_outro != 's':
            break

if __name__ == "__main__":
    main()
# gerar_inserts/oracle_utils.py

import cx_Oracle

def obter_conexao():
    while True:
        username = input("Digite o nome de usuário do Oracle: ")
        password = input("Digite a senha do Oracle: ")
        service_name = input("Digite o Service Name do Oracle: ")

        try:
            connection = cx_Oracle.connect(username, password, service_name)
            print("Conexão estabelecida com sucesso!")
            return connection
        except cx_Oracle.Error as error:
            print(f"Erro ao conectar: {error}")
            tentar_novamente = input("Deseja tentar conectar novamente? (s/n): ").lower()
            if tentar_novamente != 's':
                return None

def verificar_sequencia(cursor, sequence_name):
    try:
        cursor.execute(f"SELECT sequence_name FROM user_sequences WHERE sequence_name = '{sequence_name.upper()}'")
        return cursor.fetchone() is not None
    except cx_Oracle.Error as error:
        print(f"Erro ao verificar sequência: {error}")
        return False

def obter_sequencia(cursor):
    usar_sequencia = input("Deseja usar uma sequência para a primeira coluna (geralmente a chave primária)? (s/n): ").lower()
    if usar_sequencia == 's':
        while True:
            sequence_name = input("Digite o nome da sequência: ")
            if verificar_sequencia(cursor, sequence_name):
                return True, sequence_name.upper()
            else:
                print(f"A sequência '{sequence_name}' não foi encontrada.")
                tentar_novamente = input("Deseja tentar novamente? (s/n): ").lower()
                if tentar_novamente != 's':
                    return False, None
    return False, None
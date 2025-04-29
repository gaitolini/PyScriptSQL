import cx_Oracle
from datetime import datetime
import re  # Para extrair o nome da tabela da query

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

def obter_nome_tabela(query):
    match = re.search(r'FROM\s+(\w+(\.\w+)?)\s*', query, re.IGNORECASE)
    if match:
        return match.group(1).split('.')[-1].upper()
    return "TABELA_DESCONHECIDA"

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

def gerar_script_carga(connection, query, nome_responsavel, usar_sequencia, sequence_name):
    output_filename = f"carga_padrao_{obter_nome_tabela(query).lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            table_name = obter_nome_tabela(query)

            with open(output_filename, "w") as sql_file:
                # Cabeçalho do script
                sql_file.write(f"prompt  ...... incluindo registros padrões para {table_name}\n")
                sql_file.write(f"Rem  ---------------------------------------------------------------------------\n")
                sql_file.write(f"Rem  {nome_responsavel} em {datetime.now().strftime('%B')}/{datetime.now().strftime('%Y')}\n")
                sql_file.write(f"Rem  Geração de INSERTs para a tabela {table_name} com base na query: {query}\n")

                # Detalhes do script
                for row in rows:
                    values = []
                    for value in row:
                        if value is None:
                            values.append("NULL")
                        else:
                            if isinstance(value, str):
                                values.append(f"'{value.replace('\'', '\'\'')}'") # Escape para aspas simples
                            else:
                                values.append(str(value))

                    values_str = ", ".join(values)
                    columns_str = ", ".join(columns)

                    if usar_sequencia and columns and columns[0]: # Assume a primeira coluna é para a sequência
                        sql_insert = f"""
BEGIN
  INSERT INTO {table_name}
    ({columns_str})
  VALUES
    ({sequence_name}.NEXTVAL, {values_str.replace(values[0] + ', ', '', 1)});
  COMMIT;
EXCEPTION
  WHEN DUP_VAL_ON_INDEX THEN
    NULL;
END;
/
"""
                    else:
                        sql_insert = f"""
BEGIN
  INSERT INTO {table_name}
    ({columns_str})
  VALUES
    ({values_str});
  COMMIT;
EXCEPTION
  WHEN DUP_VAL_ON_INDEX THEN
    NULL;
END;
/
"""
                    sql_file.write(sql_insert)

                # Footer do script
                sql_file.write("\nSET DEFINE ON;\n")

            print(f"Script SQL gerado com sucesso no arquivo: {output_filename}")
            return True

    except cx_Oracle.Error as error:
        print(f"Erro ao executar a query: {error}")
        return False

if __name__ == "__main__":
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

            if gerar_script_carga(connection, query_usuario, nome_responsavel, usar_sequencia, sequence_name):
                nome_responsavel_anterior = nome_responsavel # Sugere o último nome usado

        connection.close()

        gerar_outro = input("Deseja gerar outro script SQL? (s/n): ").lower()
        if gerar_outro != 's':
            break
# gerar_inserts/campos.py

from datetime import datetime
import cx_Oracle

def obter_comentario_campo(cursor, nome_tabela, nome_campo):
    """Obtém o comentário de um campo específico no Oracle."""
    try:
        cursor.execute(f"""
            SELECT comments
            FROM user_col_comments
            WHERE table_name = '{nome_tabela.upper()}'
            AND column_name = '{nome_campo.upper()}'
        """)
        resultado = cursor.fetchone()
        if resultado and resultado[0]:
            return resultado[0]
        return None  # Retorna None se não houver comentário
    except cx_Oracle.Error as error:
        print(f"Erro ao buscar comentário para {nome_campo} na tabela {nome_tabela}: {error}")
        return None

def gerar_script_inclusao_campos(connection, query, nome_tabela):
    output_filename = f"carga_a_campos_{nome_tabela.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            if not columns:
                print("A query não retornou nenhuma coluna.")
                return

            with open(output_filename, "w") as sql_file:
                sql_file.write(f"-- Script para inclusão na tabela A_CAMPOS para a tabela {nome_tabela.upper()} gerado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                for column_name in columns:
                    comentario = obter_comentario_campo(cursor, nome_tabela, column_name)
                    field_alias = comentario if comentario else column_name.replace("_", " ").title()
                    data_type = 'VARCHAR2(255)'  # Você pode tentar obter o tipo de dado também, se necessário

                    sql_script = f"""
BEGIN
  INSERT INTO A_CAMPOS (TABLENAME, FIELDNAME, FIELDALIAS, DATATYPE, COMENTARIO)
  VALUES ('{nome_tabela.upper()}', '{column_name.upper()}', '{field_alias.replace("'", "''")}', '{data_type}', '{comentario.replace("'", "''") if comentario else field_alias.replace("'", "''")}');
  COMMIT;
EXCEPTION
  WHEN DUP_VAL_ON_INDEX THEN
    NULL;
  WHEN OTHERS THEN
    RAISE;
END;
/
"""
                    sql_file.write(sql_script + "\n")
            print(f"\nScripts de inclusão para A_CAMPOS para a tabela {nome_tabela.upper()} gerados com sucesso no arquivo: {output_filename}")

    except cx_Oracle.Error as error:
        print(f"Erro ao executar a query: {error}")
    except Exception as error:
        print(f"Ocorreu um erro: {error}")

def obter_informacoes_campos(connection):
    nome_tabela = input("Digite o nome da tabela para os campos: ").strip().upper()
    query_campos = input(f"Digite a query SELECT para obter os campos da tabela {nome_tabela} (ex: SELECT column_name FROM user_tab_cols WHERE table_name = '{nome_tabela}'): ").strip()
    return nome_tabela, query_campos
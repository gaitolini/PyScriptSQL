# gerar_inserts/campos.py

from datetime import datetime
import cx_Oracle
import re

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

def obter_nome_tabela_da_query(query):
    """Extrai o nome da tabela principal da cláusula FROM de uma query."""
    match = re.search(r'FROM\s+(\w+(\.\w+)?)\s*', query, re.IGNORECASE)
    if match:
        return match.group(1).split('.')[-1].upper()
    return None

def obter_detalhes_number(cursor, nome_tabela, nome_campo):
    """Obtém detalhes de precisão e escala para campos NUMBER."""
    try:
        cursor.execute(f"""
            SELECT data_precision, data_scale
            FROM user_tab_cols
            WHERE table_name = '{nome_tabela.upper()}'
            AND column_name = '{nome_campo.upper()}'
        """)
        resultado = cursor.fetchone()
        if resultado:
            precision = resultado[0]
            scale = resultado[1]
            if precision is not None:
                if scale is not None and scale > 0:
                    return f'NUMBER({precision},{scale})'
                else:
                    return f'NUMBER({precision})'
            else:
                return 'NUMBER'
        return 'NUMBER'
    except cx_Oracle.Error as error:
        print(f"Erro ao buscar detalhes do NUMBER para {nome_campo} na tabela {nome_tabela}: {error}")
        return 'NUMBER'

from cx_Oracle import DbType

from cx_Oracle import DbType

from cx_Oracle import DbType
from cx_Oracle import DbType

def gerar_script_inclusao_campos(cursor, query):
    nome_tabela = obter_nome_tabela_da_query(query)
    if not nome_tabela:
        print("Não foi possível identificar o nome da tabela na query.")
        return

    output_filename = f"carga_a_campos_{nome_tabela.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

    try:
        cursor.execute(query)
        columns_info = cursor.description
        if not columns_info:
            print("A query não retornou nenhuma coluna.")
            return

        with open(output_filename, "w") as sql_file:
            sql_file.write(f"-- Script para inclusão na tabela A_CAMPOS para a tabela {nome_tabela.upper()} gerado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            data_type_str = 'VARCHAR2(255)'  # Valor padrão inicial
            for col_info in columns_info:
                column_name = col_info[0]
                data_type_raw = col_info[1]  # Tipo base do Oracle
                print(f"DEBUG: Campo: {column_name}, data_type_raw: {data_type_raw}")
                comentario = obter_comentario_campo(cursor, nome_tabela, column_name)
                field_alias = comentario if comentario else column_name.replace("_", " ").title()

                if data_type_raw == DbType.DB_TYPE_NUMBER:
                    data_type_str = obter_detalhes_number(cursor, nome_tabela, column_name)
                elif data_type_raw in [DbType.DB_TYPE_VARCHAR, DbType.DB_TYPE_CHAR]:
                    data_length = obter_tamanho_varchar(cursor, nome_tabela, column_name)
                    data_type_str = f'VARCHAR2({data_length})'
                elif data_type_raw in [DbType.DB_TYPE_DATE, DbType.DB_TYPE_TIMESTAMP]:
                    data_type_str = 'DATE'
                elif data_type_raw == DbType.DB_TYPE_CLOB:
                    data_type_str = 'CLOB'
                # Adicione mais mapeamentos conforme necessário

                sql_script = f"""
BEGIN
  INSERT INTO A_CAMPOS
    (TABLENAME, FIELDNAME, FIELDALIAS, DATATYPE, COMENTARIO)
  VALUES
    ('{nome_tabela.upper()}', '{column_name.upper()}', '{field_alias.replace("'", "''")}', '{data_type_str}', '{comentario.replace("'", "''") if comentario else field_alias.replace("'", "''")}');
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

def obter_tamanho_varchar(cursor, nome_tabela, nome_campo):
    """Obtém o tamanho de um campo VARCHAR2."""
    try:
        cursor.execute(f"""
            SELECT data_length
            FROM user_tab_cols
            WHERE table_name = '{nome_tabela.upper()}'
            AND column_name = '{nome_campo.upper()}'
        """)
        resultado = cursor.fetchone()
        if resultado and resultado[0]:
            return resultado[0]
        return 255  # Retorno padrão caso não encontre ou erro
    except cx_Oracle.Error as error:
        print(f"Erro ao buscar tamanho do VARCHAR2 para {nome_campo} na tabela {nome_tabela}: {error}")
        return 255

def obter_informacoes_campos(connection):
    query_campos = input("Digite a query SELECT para obter os campos da tabela (ex: SELECT column_name FROM sua_tabela): ").strip()
    return query_campos
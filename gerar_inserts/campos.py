# gerar_inserts/campos.py

from datetime import datetime
import cx_Oracle

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
                    # Por padrão, FIELDALIAS e COMENTARIO serão baseados no FIELDNAME
                    field_alias = column_name.replace("_", " ").title()
                    comentario = field_alias

                    sql_script = f"""
BEGIN
  INSERT INTO A_CAMPOS (TABLENAME, FIELDNAME, FIELDALIAS, DATATYPE, COMENTARIO)
  VALUES ('{nome_tabela.upper()}', '{column_name.upper()}', '{field_alias}', 'VARCHAR2(255)', '{comentario}');
  COMMIT;
EXCEPTION
  WHEN DUP_VAL_ON_INDEX THEN
    NULL;
  WHEN OTHERS THEN
    RAISE
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
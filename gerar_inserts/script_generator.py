# gerar_inserts/script_generator.py

from datetime import datetime
import re

def obter_nome_tabela(query):
    match = re.search(r'FROM\s+(\w+(\.\w+)?)\s*', query, re.IGNORECASE)
    if match:
        return match.group(1).split('.')[-1].upper()
    return "TABELA_DESCONHECIDA"

def gerar_script_carga(cursor, query, nome_responsavel, usar_sequencia, sequence_name):
    output_filename = f"carga_padrao_{obter_nome_tabela(query).lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        table_name = obter_nome_tabela(query)

        with open(output_filename, "w") as sql_file:
            # Cabeçalho do script
            sql_file.write(f"prompt  ...... incluindo registros padrões para {table_name}\n")
            sql_file.write(f"Rem ---------------------------------------------------------------------------\n")
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
  INSERT INTO {table_name} ({columns_str})
  VALUES ({sequence_name}.NEXTVAL, {values_str.replace(values[0] + ', ', '', 1)});
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
  INSERT INTO {table_name} ({columns_str})
  VALUES ({values_str});
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

    except Exception as error: # Captura exceções mais genéricas aqui
        print(f"Erro ao executar a query ou gerar o script: {error}")
        return False
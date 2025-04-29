# gerar_inserts/tabelas.py

from datetime import datetime

def gerar_script_inclusao_tabela(connection):
    output_filename = f"carga_a_tabelas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    tabelas_info = []

    print("\n--- Inclusão na tabela A_TABELAS ---")
    print("Digite as informações da tabela (ou 'fim' para encerrar):")

    while True:
        nome_tabela = input("Nome da Tabela: ").strip().upper()
        if nome_tabela == 'FIM':
            break
        descricao = input("Descrição da Tabela: ").strip()
        sistema = input("Sistema (0-Oculto, 1-Contábil, 2-Industrial, 3-Ambos): ").strip()
        if sistema not in ['0', '1', '2', '3']:
            print("Valor de sistema inválido. Use 0, 1, 2 ou 3.")
            continue
        tabelas_info.append((nome_tabela, descricao, sistema))

    if tabelas_info:
        with open(output_filename, "w") as sql_file:
            sql_file.write(f"-- Script para inclusão na tabela A_TABELAS gerado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for nome_tabela, descricao, sistema in tabelas_info:
                sql_script = f"""
BEGIN
  INSERT INTO A_TABELAS
    (TABLENAME, TABLEALIAS, TABLETIPO)
  VALUES
    ('{nome_tabela}', '{descricao.replace("'", "''")}', '{sistema}');
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
        print(f"\nScripts de inclusão para A_TABELAS gerados com sucesso no arquivo: {output_filename}")
    else:
        print("Nenhuma informação de tabela foi fornecida.")
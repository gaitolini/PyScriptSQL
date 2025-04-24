🚀 Gerador de Scripts SQL Automatizado para Oracle
Este projeto tem como objetivo simplificar e automatizar a criação de scripts SQL para o banco de dados Oracle, focando na eficiência e economia de tempo. Com ele, você pode gerar blocos de comandos INSERT com tratamento de exceção a partir de consultas SQL diretamente no seu terminal com um simples clique.

✨ A ideia é automatizar tarefas repetitivas e ganhar mais tempo para o que realmente importa! ✨

🛠️ Pré-requisitos
Para utilizar o Gerador de Scripts SQL, você precisa ter o Python instalado na sua máquina. O arquivo executar_gerador_sql.bat tentará verificar e, se necessário, instalar automaticamente tanto o Python quanto a biblioteca cx_Oracle necessária para este projeto.

Caso a instalação automática falhe ou se você preferir gerenciar as instalações manualmente, siga as instruções abaixo:

Python (Instalação Manual):

Windows:

Acesse o site oficial do Python: https://www.python.org/downloads/windows/
Baixe a versão mais recente do Python 3.
Execute o instalador e marque a opção "Add Python to PATH" durante a instalação. Isso é importante para que você possa executar o Python a partir do terminal.
Siga as instruções do instalador para completar a instalação.
macOS:

O macOS geralmente vem com o Python pré-instalado, mas pode ser uma versão mais antiga. É recomendado instalar a versão mais recente através do site oficial: https://www.python.org/downloads/macos/
Baixe o instalador e siga as instruções.
Linux:

A instalação do Python varia dependendo da sua distribuição Linux. Geralmente, você pode usar o gerenciador de pacotes da sua distribuição.
Abra o terminal e execute o comando apropriado (exemplo para Debian/Ubuntu):
Bash

sudo apt update
sudo apt install python3
Após a instalação, verifique a versão do Python com o comando: python3 --version
cx_Oracle (Instalação Manual): Esta é a biblioteca Python necessária para conectar e interagir com o banco de dados Oracle. Caso a instalação automática pelo .bat não funcione, você pode instalá-la manualmente usando o pip (gerenciador de pacotes do Python) no seu terminal:

Bash

pip install cx_Oracle
Certifique-se de ter o Oracle Client instalado na sua máquina, pois o cx_Oracle depende dele para se conectar ao banco de dados Oracle.

🚀 Como Usar
Salve os arquivos: Salve o script Python como gerar_inserts.py e o arquivo Batch como executar_gerador_sql.bat na mesma pasta.

gerar_inserts.py (Conteúdo do script Python):

Python

import cx_Oracle
from datetime import datetime
import re

def obter_conexiao():
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
                sql_file.write(f"prompt  ...... incluindo registros padrões para {table_name}\n")
                sql_file.write(f"Rem ---------------------------------------------------------------------------\n")
                sql_file.write(f"Rem  {nome_responsavel} em {datetime.now().strftime('%B')}/{datetime.now().strftime('%Y')}\n")
                sql_file.write(f"Rem  Geração de INSERTs para a tabela {table_name} com base na query: {query}\n")

                for row in rows:
                    values = []
                    for value in row:
                        if value is None:
                            values.append("NULL")
                        else:
                            if isinstance(value, str):
                                values.append(f"'{value.replace('\'', '\'\'')}'")
                            else:
                                values.append(str(value))

                    values_str = ", ".join(values)
                    columns_str = ", ".join(columns)

                    if usar_sequencia and columns and columns[0]:
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

                sql_file.write("\nSET DEFINE ON;\n")

            print(f"Script SQL gerado com sucesso no arquivo: {output_filename}")
            return True

    except cx_Oracle.Error as error:
        print(f"Erro ao executar a query: {error}")
        return False

if __name__ == "__main__":
    nome_responsavel_anterior = ""

    while True:
        connection = obter_conexiao()
        if not connection:
            print("Não foi possível estabelecer conexão. Encerrando.")
            break

        nome_responsavel = input(f"Digite o nome do responsável pela geração do script (pressione Enter para usar: {nome_responsavel_anterior}): ") or nome_responsavel_anterior
        query_usuario = input(f"Digite a query SELECT para extrair os dados (ex: SELECT * FROM SUA_TABELA WHERE ...): ")

        with connection.cursor() as cursor:
            usar_sequencia, sequence_name = obter_sequencia(cursor)

            if gerar_script_carga(connection, query_usuario, nome_responsavel, usar_sequencia, sequence_name):
                nome_responsavel_anterior = nome_responsavel

        connection.close()

        gerar_outro = input("Deseja gerar outro script SQL? (s/n): ").lower()
        if gerar_outro != 's':
            break
executar_gerador_sql.bat (Conteúdo do arquivo Batch):

Snippet de código

@echo off
echo Iniciando o Gerador de Scripts SQL...

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python não foi encontrado.
    echo Por favor, certifique-se de que o Python esteja instalado e no PATH do sistema.
    echo Siga as instruções no README.md para instalação.
    pause
    exit /b 1
)

python -m pip show cx_Oracle >nul 2>&1
if %errorlevel% neq 0 (
    echo A biblioteca cx_Oracle não foi encontrada.
    echo Tentando instalar a biblioteca cx_Oracle...
    python -m pip install cx_Oracle
    if %errorlevel% neq 0 (
        echo ERRO: Falha ao instalar a biblioteca cx_Oracle.
        echo Por favor, verifique sua conexão com a internet ou instale manualmente com 'pip install cx_Oracle'.
        pause
        exit /b 1
    )
)

echo Executando o script...
python gerar_inserts.py
echo Script finalizado.

echo.
echo -----------------------------------------------------------------------
echo Criado por Anderson Gaitolini / github.com\gaitolini
echo -----------------------------------------------------------------------
pause
exit /b 0
Execute o arquivo .bat: Dê um duplo clique no arquivo executar_gerador_sql.bat.

Siga as instruções: O script Batch tentará automaticamente verificar e instalar o Python (se não encontrado) e a biblioteca cx_Oracle. Certifique-se de ter uma conexão com a internet durante esta etapa. Em caso de falha na instalação automática, o script exibirá mensagens orientando sobre a instalação manual do Python e da biblioteca cx_Oracle. Uma vez que os pré-requisitos estejam instalados, o script Python gerar_inserts.py será executado, solicitando as informações necessárias para gerar o script SQL.

🤝 Ajuda é Bem-Vinda!
Este é um projeto criado por Anderson Gaitolini (github.com/gaitolini) com o objetivo de automatizar e otimizar o fluxo de trabalho SQL, economizando tempo e aumentando a eficiência.

Toda ajuda é bem-vinda! Se você tiver ideias para melhorar o script, encontrar bugs ou quiser adicionar novas funcionalidades, sinta-se à vontade para contribuir. Podemos tornar a gestão do tempo ainda mais eficiente juntos!

Compartilhe suas sugestões e ideias abrindo uma Issue neste repositório.
Se você tem conhecimento em Python e Oracle, envie suas Pull Requests com melhorias e novas funcionalidades.
✨ Vamos automatizar e otimizar nosso fluxo de trabalho SQL! ✨
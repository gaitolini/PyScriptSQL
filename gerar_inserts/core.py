# gerar_inserts/core.py

def gerar_comandos_insert(dados):
    """
    Gera comandos SQL INSERT a partir dos dados fornecidos.
    """
    comandos_sql = []
    for linha in dados:
        # Adapte esta parte de acordo com a estrutura dos seus dados
        tabela = "sua_tabela"
        colunas = "coluna1, coluna2, coluna3"
        valores = f"'{linha['valor1']}', '{linha['valor2']}', '{linha['valor3']}'"
        comando = f"INSERT INTO {tabela} ({colunas}) VALUES ({valores});"
        comandos_sql.append(comando)
    return comandos_sql

def salvar_comandos(comandos, nome_arquivo="inserts.sql"):
    """
    Salva os comandos SQL em um arquivo.
    """
    with open(nome_arquivo, "w") as arquivo:
        for comando in comandos:
            arquivo.write(comando + "\n")
    print(f"Comandos SQL salvos em: {nome_arquivo}")

# Exemplo de como essa função poderia ser chamada
if __name__ == "__main__":
    dados_exemplo = [
        {"valor1": "A", "valor2": 1, "valor3": "X"},
        {"valor1": "B", "valor2": 2, "valor3": "Y"}
    ]
    comandos = gerar_comandos_insert(dados_exemplo)
    salvar_comandos(comandos)
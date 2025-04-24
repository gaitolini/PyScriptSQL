@echo off
echo Verificando se o Python está instalado...
where python
if %errorlevel% == 0 (
    echo Python encontrado.
    echo Verificando se a biblioteca cx_Oracle está instalada...
    python -m pip show cx_Oracle
    if %errorlevel% == 0 (
        echo cx_Oracle encontrado. Iniciando o script...
        python gerar_inserts.py
        pause
    ) else (
        echo A biblioteca cx_Oracle não está instalada.
        echo Deseja tentar instalar agora? (s/n)
        set /p resposta=
        if /i "%resposta%" == "s" (
            echo Tentando instalar a biblioteca cx_Oracle...
            python -m pip install cx_Oracle
            if %errorlevel% == 0 (
                echo Biblioteca cx_Oracle instalada com sucesso. Iniciando o script...
                python gerar_inserts.py
                pause
            ) else (
                echo Falha ao instalar a biblioteca cx_Oracle.
                echo Por favor, verifique sua conexão com a internet e tente novamente.
                echo Você também pode tentar executar o comando 'pip install cx_Oracle' manualmente no terminal.
                pause
            )
        ) else (
            echo Instalação da biblioteca cx_Oracle cancelada.
            echo Por favor, instale-a manualmente usando o comando 'pip install cx_Oracle' no terminal.
            pause
        )
    )
) else (
    echo Python não foi encontrado no sistema.
    echo Por favor, instale o Python seguindo as instruções no README.md.
    echo Após a instalação, execute este arquivo .bat novamente.
    pause
)
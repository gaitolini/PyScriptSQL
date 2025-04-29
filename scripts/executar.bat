@echo off
echo Iniciando o Gerador de Scripts SQL (CLI)...

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

echo Executando o script CLI...
python -m gerar_inserts.cli
echo Script finalizado.

echo.
echo -----------------------------------------------------------------------
echo Criado por Anderson Gaitolini / github.com\gaitolini
echo -----------------------------------------------------------------------
pause
exit /b 0
@echo off
REM Script para iniciar o backend no Windows

REM Verifica se o virtual environment existe
if not exist "venv" (
    echo Criando virtual environment...
    python -m venv venv
)

REM Ativa o virtual environment
call venv\Scripts\activate

REM Instala as dependências se o requirements.txt existir
if exist "requirements.txt" (
    echo Instalando dependências...
    pip install -r requirements.txt
)

REM Inicia o servidor Flask
echo Iniciando servidor Flask...
python app.py

REM Mantém a janela aberta
pause
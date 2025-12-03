@echo off
TITLE Servidor de Gestão de Alunos (Produção)
COLOR 0B
echo ===================================================
echo  INICIANDO SERVIDOR DE PRODUCAO (WAITRESS)
echo  Acesse em: http://localhost:5000
echo ===================================================
echo.
echo Pressione Ctrl+C nesta janela para parar o servidor.
echo.
:: 'app:app' significa "procure no arquivo app.py pela variável app"
:: ⭐️⭐️ NOVO: Adicionado --channel-timeout=600 (10 minutos) para tarefas longas de IA ⭐️⭐️
waitress-serve --host=0.0.0.0 --port=5000 --channel-timeout=300 app:app

echo Servidor encerrado.
pause > nul
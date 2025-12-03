# run.py

from app import create_app
from app.models.base_legacy import db 

# 1. Cria a instância da aplicação usando a Application Factory
# Isso carrega a configuração e registra todas as extensões e rotas.
app = create_app() 

# 2. Bloco de execução principal para iniciar o servidor de desenvolvimento
if __name__ == '__main__':
    # Garante que as tabelas da base de dados existam antes de executar a aplicação.
    with app.app_context():
        db.create_all()
        
    # Inicia o servidor Flask em modo de depuração.
    app.run(debug=True)
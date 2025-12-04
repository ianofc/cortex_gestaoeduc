# run.py

from app import create_app
# CORREÇÃO: Importar de 'app.models' em vez de 'app.models.base_legacy'
from app.models import db 

# 1. Cria a instância da aplicação usando a Application Factory
app = create_app() 

# 2. Bloco de execução principal
if __name__ == '__main__':
    with app.app_context():
        # Isso cria as tabelas baseadas nos modelos importados em app.models
        db.create_all()
        
    app.run(debug=True)
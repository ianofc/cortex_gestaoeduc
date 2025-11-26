# app.py

import os
from flask import Flask
from config import Config

# Imports de extensões Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_moment import Moment
from flask_migrate import Migrate


# --- NOVO: Instância Bcrypt Global ---
# Inicializa a instância do Bcrypt globalmente.
# Isso garante que a instância seja única e acessível via current_app.extensions['bcrypt']
bcrypt = Bcrypt() 


# Imports de Módulos Locais (Modelos e Blueprints)
from models import db, User 
from blueprints.auth import auth_bp
from blueprints.core import core_bp
from blueprints.planos import planos_bp
from blueprints.alunos import alunos_bp


# --- APPLICATION FACTORY ---

def create_app(config_class=Config):
    """Cria e configura a instância da aplicação Flask."""
    
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 1. Inicialização de Extensões
    db.init_app(app)
    bcrypt.init_app(app) # CORREÇÃO: Usa init_app no objeto global 'bcrypt'
    Moment(app) 
    Migrate(app, db)
    
    # Configura o Flask-Login
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login' # Aponta para a rota login no Blueprint 'auth'
    login_manager.login_message = 'Por favor, faça o login para acessar esta página.'
    login_manager.login_message_category = 'info' 

    # 2. User Loader (Necessário para o Flask-Login)
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 3. Configuração da Pasta de Upload 
    UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # 4. Registro dos Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(core_bp)
    app.register_blueprint(planos_bp)
    app.register_blueprint(alunos_bp)
    
    return app

# A variável 'app' global é necessária para o 'run.py', 'waitress-serve' e comandos CLI.
app = create_app()


# --- COMANDOS CLI (FLASK COMMANDS) ---

@app.cli.command("create-db-full")
def create_db_full():
    """Cria o banco de dados e as tabelas se não existirem."""
    with app.app_context():
        db.create_all()
        print(">>> Banco de dados (SQLite) e tabelas verificados/criados com sucesso!")

@app.cli.command("reset-db-full")
def reset_db_full():
    """Deleta e recria TODAS as tabelas. PERIGO: PERDE TODOS OS DADOS."""
    with app.app_context():
        try:
            print("Iniciando reset COMPLETO do banco de dados...")
            db.drop_all()
            print("Tabelas antigas deletadas.")
            db.create_all()
            print("✅ Sucesso! Banco de dados limpo e recriado.")
        except Exception as e:
            print(f"❌ Erro durante o reset: {e}")
import os
from flask import Flask
from config import Config

# Imports de extensões Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_moment import Moment
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect 

# --- Instâncias Globais ---
bcrypt = Bcrypt()
csrf = CSRFProtect()

# Imports de Módulos Locais
from models import db, User 
from blueprints.auth import auth_bp
from blueprints.core import core_bp
from blueprints.planos import planos_bp
from blueprints.alunos import alunos_bp
from blueprints.backup import backup_bp
from blueprints.portal import portal_bp # <--- NOVO IMPORT

# --- APPLICATION FACTORY ---

def create_app(config_class=Config):
    """Cria e configura a instância da aplicação Flask."""
    
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 1. Inicialização de Extensões
    db.init_app(app)
    bcrypt.init_app(app)
    Moment(app) 
    Migrate(app, db)
    csrf.init_app(app)
    
    # Configura o Flask-Login
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça o login para acessar esta página.'
    login_manager.login_message_category = 'info' 

    # 2. User Loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 3. Configuração da Pasta de Upload 
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        try:
            os.makedirs(app.config['UPLOAD_FOLDER'])
        except OSError as e:
            print(f"Erro ao criar pasta de upload: {e}")

    # 4. Registro dos Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(core_bp)
    app.register_blueprint(planos_bp)
    app.register_blueprint(alunos_bp)
    app.register_blueprint(backup_bp)
    app.register_blueprint(portal_bp) # <--- REGISTRO DO PORTAL
    
    return app

# A variável 'app' global
app = create_app()

# --- COMANDOS CLI ---

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
import os
from flask import Flask
from config import Config

# Imports de extensões Flask
from flask_login import LoginManager, current_user # Adicionado current_user
from flask_moment import Moment
from flask_migrate import Migrate

# --- IMPORTAÇÃO DAS EXTENSÕES ---
# (Ajustado para a nova pasta 'app')
from app.extensions import bcrypt, csrf 

# Imports de Módulos Locais (Ajustados para a nova estrutura)
# O models.py original virou app.models.base_legacy na migração
from app.models.base_legacy import db, User, Notificacao 
from app.blueprints.auth import auth_bp
from app.blueprints.core import core_bp
from app.blueprints.planos import planos_bp
from app.blueprints.alunos import alunos_bp
from app.blueprints.backup import backup_bp
from app.blueprints.portal import portal_bp 

# Tenta importar a coordenação (novo módulo)
try:
    from app.blueprints.coordenacao import coordenacao_bp
except ImportError:
    coordenacao_bp = None

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

    # --- CORREÇÃO: CONTEXT PROCESSOR GLOBAL ---
    # Isso garante que 'num_notificacoes' exista em TODAS as páginas
    @app.context_processor
    def inject_notificacoes():
        if current_user.is_authenticated:
            try:
                # Conta notificações não lidas
                nao_lidas = Notificacao.query.filter_by(destinatario=current_user, lida=False).count()
                # Pega as 5 mais recentes
                recentes = Notificacao.query.filter_by(destinatario=current_user).order_by(Notificacao.data_criacao.desc()).limit(5).all()
                return dict(num_notificacoes=nao_lidas, notificacoes_topo=recentes)
            except Exception:
                # Proteção caso a tabela Notificacao ainda não tenha sido criada
                return dict(num_notificacoes=0, notificacoes_topo=[])
        return dict(num_notificacoes=0, notificacoes_topo=[])

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
    app.register_blueprint(portal_bp)
    
    # Registro condicional da Coordenação
    if coordenacao_bp:
        app.register_blueprint(coordenacao_bp)
    
    return app

# A variável 'app' global
app = create_app()

# --- COMANDOS CLI ---

@app.cli.command("create-db-full")
def create_db_full():
    with app.app_context():
        db.create_all()
        print(">>> Banco de dados verificado/criado!")

@app.cli.command("reset-db-full")
def reset_db_full():
    with app.app_context():
        try:
            print("Resetando banco...")
            db.drop_all()
            db.create_all()
            print("✅ Sucesso!")
        except Exception as e:
            print(f"❌ Erro: {e}")
from flask import Flask
# Corrigido: Incluído bcrypt e csrf nas extensões
from .extensions import db, login_manager, migrate, bcrypt, csrf 
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 1. Inicializar Extensões (Banco, Login, Migração, Segurança)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app) # Inicializa Bcrypt
    csrf.init_app(app) # Inicializa CSRF
    
    # Configuração da view de login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # CORREÇÃO: User Loader (Para Flask-Login)
    @login_manager.user_loader
    def load_user(user_id):
        # Importação mais específica para evitar Circular Import
        from app.models.users import User 
        return User.query.get(int(user_id))

    # --- CORREÇÃO FINAL: REGISTRO GLOBAL DO CONTEXT PROCESSOR ---
    # Isso injeta num_notificacoes e notificacoes_topo em TODOS os templates.
    from app.blueprints.core import inject_notifications_logic
    app.context_processor(inject_notifications_logic)
    # -----------------------------------------------------------

    # 2. Registrar Blueprints
    
    # --- Autenticação (Rotas de Login/Registro) ---
    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # --- API (Isento de CSRF) ---
    from app.blueprints.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    csrf.exempt(api_bp) # Isenta de CSRF Token

    # --- Admin / Core (Rotas principais e de administração) ---
    from app.blueprints.core import core_bp
    app.register_blueprint(core_bp) 

    # --- Gestão de Secretaria / Alunos ---
    from app.blueprints.alunos import alunos_bp
    app.register_blueprint(alunos_bp, url_prefix='/alunos')

    # --- Professor (Planejamento) ---
    from app.blueprints.planos import planos_bp
    app.register_blueprint(planos_bp, url_prefix='/planejamento') 
    
    # --- PORTAL DO PROFESSOR (Dashboard) ---
    try:
        from app.blueprints.professor import professor_bp
        app.register_blueprint(professor_bp, url_prefix='/professor') # Rota: /professor/dashboard
    except ImportError as e:
        print(f"⚠️ Aviso: Módulo do Professor não carregado: {e}")

    # --- Portal do Aluno ---
    from app.blueprints.portal import portal_bp
    app.register_blueprint(portal_bp, url_prefix='/portal') # Rota: /portal/dashboard

    # --- Segurança e Backup ---
    from app.blueprints.backup import backup_bp
    app.register_blueprint(backup_bp, url_prefix='/backup')

    # --- Coordenação ---
    try:
        from app.blueprints.coordenacao import coordenacao_bp
        app.register_blueprint(coordenacao_bp, url_prefix='/coordenacao') # Rota: /coordenacao/dashboard
    except ImportError as e:
        print(f"⚠️ Aviso: Módulo de Coordenação não carregado: {e}")

    return app
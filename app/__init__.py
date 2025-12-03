from flask import Flask
from .extensions import db, login_manager, migrate
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 1. Inicializar Extensões (Banco, Login, Migração)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # 2. Registrar Blueprints (Os "Lobos" do Cérebro)
    
    # --- Autenticação (Porta de Entrada) ---
    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)

    # --- Admin / Direção (Antigo 'Core') ---
    # Gerencia dashboards globais e configurações
    from app.blueprints.core import core_bp
    app.register_blueprint(core_bp) 

    # --- Gestão de Secretaria (Cadastros) ---
    from app.blueprints.alunos import alunos_bp
    app.register_blueprint(alunos_bp)

    # --- Professor (Pedagógico/Planos) ---
    from app.blueprints.planos import planos_bp
    app.register_blueprint(planos_bp)

    # --- Portal do Aluno (Visualização) ---
    from app.blueprints.portal import portal_bp
    app.register_blueprint(portal_bp)

    # --- Segurança e Backup ---
    from app.blueprints.backup import backup_bp
    app.register_blueprint(backup_bp)

    # --- Coordenação (NOVO MÓDULO) ---
    # Envolvemos em try/except para o sistema não quebrar 
    # caso o arquivo coordenacao.py ainda não tenha sido criado corretamente
    try:
        from app.blueprints.coordenacao import coordenacao_bp
        app.register_blueprint(coordenacao_bp)
    except ImportError as e:
        print(f"⚠️ Aviso: Módulo de Coordenação não carregado: {e}")

    return app
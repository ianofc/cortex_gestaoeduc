
from flask import Flask
from .extensions import db, login_manager, migrate
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar Extensões
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Registrar Blueprints (Você precisará atualizar os imports dentro deles)
    # from app.blueprints.core import core_bp
    # app.register_blueprint(core_bp)

    return app

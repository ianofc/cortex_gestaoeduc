import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

class Config:
    # Configurações de Banco de Dados
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR}/gestao_alunos.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Segurança
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    
    # --- UPLOADS SEM LIMITES RÍGIDOS ---
    # Define o caminho absoluto para static/uploads
    UPLOAD_FOLDER = str(BASE_DIR / 'static' / 'uploads')
    
    # Aumentando o limite para 1GB (permite vídeos, múltiplos PDFs, imagens em alta def)
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024 
    
    # API Key
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
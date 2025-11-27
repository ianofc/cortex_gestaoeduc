import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
# BASE_DIR é a pasta raiz onde estão app.py, config.py, etc.
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

class Config:
    # --- Banco de Dados ---
    # Garante caminho absoluto para o SQLite
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'gestao_alunos.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- Segurança ---
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    
    # --- Uploads (CRÍTICO PARA BACKUP) ---
    # Define explicitamente static/uploads como o local correto dos arquivos
    # Usando string pura para compatibilidade com Flask
    UPLOAD_FOLDER = str(BASE_DIR / 'static' / 'uploads')
    
    # Limite de Upload (1GB para suportar vídeos/PDFs grandes)
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024 
    
    # API Key IA
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
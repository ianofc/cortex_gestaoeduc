import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env ANTES de qualquer outra coisa
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR}/gestao_alunos.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)
    
    # Agora, isso vai ler o valor carregado do arquivo .env
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
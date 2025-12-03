import psycopg2
import os
from dotenv import load_dotenv

load_dotenv() # Carrega o .env

url = os.getenv("DATABASE_URL")
print(f"Tentando conectar em: {url.split('@')[1]}") # Mostra só o host para segurança

try:
    conn = psycopg2.connect(url)
    print("✅ SUCESSO! Conexão com Supabase estabelecida.")
    conn.close()
except Exception as e:
    print(f"❌ ERRO: {e}")
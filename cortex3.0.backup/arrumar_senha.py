from urllib.parse import quote_plus

# 1. Digite sua senha aqui dentro das aspas (exatamente como criou no Supabase)
minha_senha = "2511CorteXEduc" 

# 2. O script vai converter os caracteres proibidos
senha_segura = quote_plus(minha_senha)

# 3. Mostra como deve ficar no arquivo .env
print("\n--- COPIE A LINHA ABAIXO PARA O SEU .ENV ---")
print(f"DATABASE_URL=postgresql://postgres:{senha_segura}@db.qnknyonohlorjfhzkkpz.supabase.co:5432/postgres")
print("----------------------------------------------\n")
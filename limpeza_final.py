import os
import shutil
from pathlib import Path

# --- CONFIGURAÇÕES DE SEGURANÇA ---
BASE_DIR = Path(".")

# Pastas e Arquivos que JAMAIS devem ser apagados (A Nova Estrutura)
ITENS_PARA_MANTER = [
    ".env",
    ".gitignore",
    "requirements.txt",
    "run.py",           # Seu novo ponto de entrada
    "config.py",        # Configurações globais
    "app",              # O NOVO CÉREBRO (Onde tudo deve estar agora)
    "instance",         # Onde fica o banco de dados (site.db / gestao_alunos.db)
    "migrations",       # Histórico do Alembic (se estiver na raiz)
    "media",            # Uploads dos usuários
    "backups",          # Seus backups locais
    ".git",             # Histórico do Git
    "limpeza_final.py", # Este script
    "README.md",
    "Procfile",         # Se usar Heroku
    "docker-compose.yml",
    "Dockerfile"
]

# Prefixos de pastas de backup que o script anterior pode ter criado
# Se você quiser apagá-las também, deixe como está. Se quiser manter, remova da lista.
PREFIXOS_LIXO = ["backup_pre_refactor", "cortex3.0.backup"] 

def confirmar_acao():
    print("!!! ATENÇÃO !!!")
    print("Este script vai APAGAR permanentemente os arquivos duplicados/antigos da raiz.")
    print("Ele manterá apenas a pasta 'app/' e arquivos de configuração.")
    print("Certifique-se de que você tem um backup seguro antes de continuar.")
    resposta = input("\nDigite 'LIMPAR' para confirmar e apagar os arquivos antigos: ")
    return resposta == "LIMPAR"

def executar_limpeza():
    print("\n🧹 Iniciando limpeza do Sistema Cortex...")
    
    itens_removidos = 0
    
    # Listar tudo no diretório atual
    for item in BASE_DIR.iterdir():
        nome = item.name
        
        # 1. Se estiver na lista de MANTER, pula
        if nome in ITENS_PARA_MANTER:
            print(f"🛡️ Mantido: {nome}")
            continue
            
        # 2. Proteção extra para pastas ocultas do sistema (ex: .vscode, .idea)
        if nome.startswith(".") and nome != ".env" and nome != ".gitignore":
            print(f"🛡️ Ignorado (Oculto): {nome}")
            continue

        # 3. Decidir se apaga
        caminho_completo = BASE_DIR / nome
        
        try:
            if caminho_completo.is_dir():
                # É uma pasta (ex: blueprints antiga, templates antiga)
                shutil.rmtree(caminho_completo)
                print(f"🗑️ Pasta Removida: {nome}/ (Versão antiga)")
                itens_removidos += 1
            elif caminho_completo.is_file():
                # É um arquivo (ex: models.py antigo, app.py antigo)
                os.remove(caminho_completo)
                print(f"🗑️ Arquivo Removido: {nome} (Versão antiga)")
                itens_removidos += 1
        except Exception as e:
            print(f"❌ Erro ao remover {nome}: {e}")

    print(f"\n✨ Limpeza concluída! {itens_removidos} itens antigos removidos.")
    print("Agora seu projeto deve ter apenas a pasta 'app/' e as configurações na raiz.")

if __name__ == "__main__":
    if confirmar_acao():
        executar_limpeza()
    else:
        print("Operação cancelada. Nada foi apagado.")
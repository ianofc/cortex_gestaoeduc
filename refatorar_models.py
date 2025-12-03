import os
import re

# Caminhos
BASE_PATH = "app/models"
LEGACY_FILE = f"{BASE_PATH}/base_legacy.py"

# Definição de onde cada classe deve morar (Regras de Negócio)
MAPA_CLASSES = {
    "User": "users.py",
    "Role": "users.py", # Se existir
    "Notificacao": "users.py",
    
    "Turma": "academic.py",
    "Aluno": "academic.py",
    "Presenca": "academic.py",
    "Horario": "academic.py",
    "BlocoAula": "academic.py",
    
    "PlanoDeAula": "pedagogical.py",
    "Atividade": "pedagogical.py",
    "DiarioBordo": "pedagogical.py",
    "Material": "pedagogical.py",
    
    "Mensalidade": "financial.py",
    "Contrato": "financial.py",
    "Boleto": "financial.py"
}

def refatorar():
    if not os.path.exists(LEGACY_FILE):
        print(f"❌ Erro: {LEGACY_FILE} não encontrado.")
        return

    print(f"📖 Lendo {LEGACY_FILE}...")
    with open(LEGACY_FILE, "r", encoding="utf-8") as f:
        conteudo = f.read()

    # Cabeçalho padrão para todos os novos arquivos (Imports do SQLAlchemy)
    header_padrao = "from app.extensions import db\nfrom datetime import datetime, date\n\n"

    arquivos_conteudo = {
        "users.py": header_padrao,
        "academic.py": header_padrao,
        "pedagogical.py": header_padrao,
        "financial.py": header_padrao,
    }

    # Expressão regular para encontrar classes inteiras
    # Procura por "class Nome(..." até a próxima "class " ou fim do arquivo
    # Nota: Isso é uma aproximação robusta para arquivos Python bem formatados
    partes = re.split(r'(^class\s+\w+[\s\(].*?:)', conteudo, flags=re.MULTILINE)

    # A parte 0 geralmente são os imports iniciais do arquivo legado
    imports_legado = partes[0] 
    
    print("⚡ Processando classes...")
    current_class_name = None
    
    for i in range(1, len(partes), 2):
        class_def = partes[i]      # ex: "class User(UserMixin, db.Model):"
        class_body = partes[i+1]   # O conteúdo da classe
        
        # Extrair nome da classe
        match = re.match(r'class\s+(\w+)', class_def)
        if match:
            class_name = match.group(1)
            destino = MAPA_CLASSES.get(class_name, "users.py") # Default para users se não mapeado
            
            # Adiciona ao arquivo destino
            texto_classe = class_def + class_body
            arquivos_conteudo[destino] += texto_classe + "\n"
            print(f"   - {class_name} -> {destino}")

    # Escrever os novos arquivos
    print("💾 Salvando novos arquivos em app/models/...")
    for nome_arquivo, conteudo_arquivo in arquivos_conteudo.items():
        caminho_final = f"{BASE_PATH}/{nome_arquivo}"
        with open(caminho_final, "w", encoding="utf-8") as f:
            f.write(conteudo_arquivo)
        print(f"   ✅ {nome_arquivo}")

    # Criar o __init__.py para expor tudo (Facade Pattern)
    # Isso permite que o resto do app continue fazendo "from app.models import User"
    print("🔗 Criando app/models/__init__.py...")
    with open(f"{BASE_PATH}/__init__.py", "w", encoding="utf-8") as f:
        f.write("from .users import *\n")
        f.write("from .academic import *\n")
        f.write("from .pedagogical import *\n")
        f.write("from .financial import *\n")
        # Opcional: expor db aqui também se o código antigo esperava
        f.write("from app.extensions import db\n")

    print("\n🏁 Refatoração Concluída!")
    print("OBS: O arquivo 'base_legacy.py' ainda existe. Verifique se tudo funciona e depois apague-o.")

if __name__ == "__main__":
    refatorar()
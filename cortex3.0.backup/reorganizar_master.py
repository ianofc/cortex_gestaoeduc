import os
import shutil
from pathlib import Path
from datetime import datetime

# --- CONFIGURAÇÕES ---
BASE_DIR = Path(".")
APP_DIR = BASE_DIR / "app"
BACKUP_DIR = BASE_DIR / f"backup_pre_refactor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Nova Estrutura de Pastas dentro de 'app/'
NEW_DIRS = [
    # Camada de Apresentação (Templates)
    "app/templates/public",
    "app/templates/auth",
    "app/templates/admin/dashboard",
    "app/templates/admin/usuarios",
    "app/templates/admin/configuracoes",
    "app/templates/admin/financeiro",
    "app/templates/professor/dashboard",
    "app/templates/professor/planejamento",
    "app/templates/professor/turma",
    "app/templates/professor/atividades",
    "app/templates/aluno",
    "app/templates/layouts",
    "app/templates/components",
    
    # Camada de Lógica (Python)
    "app/blueprints",
    "app/models",
    "app/forms",
    "app/services",  # Nova camada de serviços
    "app/utils",
    
    # Arquivos Estáticos
    "app/static/css",
    "app/static/js",
    "app/static/img",
    "app/static/vendor",
    
    # Mídia (Uploads) - Fora do app, mas organizado
    "media/docs",
    "media/imgs",
]

# Mapa de Movimentação (Origem -> Destino)
MOVE_MAP = {
    # --- TEMPLATES (Reorganização Visual) ---
    "templates/landing_page.html": "app/templates/public/landing_page.html",
    "templates/pricing.html": "app/templates/public/pricing.html",
    "templates/contact.html": "app/templates/public/contact.html",
    "templates/demo.html": "app/templates/public/demo.html",
    "templates/checkout.html": "app/templates/public/checkout.html",
    "templates/main/login.html": "app/templates/auth/login.html",
    "templates/main/register.html": "app/templates/auth/register.html",
    "templates/main/base.html": "app/templates/layouts/base_app.html",
    "templates/main/index.html": "app/templates/layouts/base_public.html",
    "templates/geral/dashboard_global.html": "app/templates/admin/dashboard/global.html",
    "templates/add/add_escola.html": "app/templates/admin/configuracoes/nova_escola.html",
    "templates/edit/edit_escola.html": "app/templates/admin/configuracoes/editar_escola.html",
    "templates/list/listar_escola.html": "app/templates/admin/configuracoes/listar_escolas.html",
    "templates/add/add_professor.html": "app/templates/admin/usuarios/novo_professor.html",
    "templates/edit/edit_professor.html": "app/templates/admin/usuarios/editar_professor.html",
    "templates/list/listar_professores.html": "app/templates/admin/usuarios/listar_professores.html",
    "templates/add/add_coordenador.html": "app/templates/admin/usuarios/novo_coordenador.html",
    "templates/edit/edit_coordenador.html": "app/templates/admin/usuarios/editar_coordenador.html",
    "templates/list/listar_coordenadores.html": "app/templates/admin/usuarios/listar_coordenadores.html",
    "templates/add/add_aluno.html": "app/templates/admin/usuarios/novo_aluno.html",
    "templates/edit/edit_aluno.html": "app/templates/admin/usuarios/editar_aluno.html",
    "templates/list/listar_alunos.html": "app/templates/admin/usuarios/listar_alunos.html",
    "templates/add/add_turma.html": "app/templates/admin/configuracoes/nova_turma.html",
    "templates/edit/edit_turma.html": "app/templates/admin/configuracoes/editar_turma.html",
    "templates/list/listar_turmas.html": "app/templates/admin/configuracoes/listar_turmas.html",
    "templates/geral/dashboard_turma.html": "app/templates/professor/dashboard/turma.html",
    "templates/geral/diario_bordo.html": "app/templates/professor/turma/diario_classe.html",
    "templates/geral/gradebook.html": "app/templates/professor/turma/gradebook.html",
    "templates/geral/registrar_presenca.html": "app/templates/professor/turma/chamada.html",
    "templates/geral/gerar_prova.html": "app/templates/professor/atividades/gerador_provas.html",
    "templates/geral/turma.html": "app/templates/professor/turma/visao_geral.html",
    "templates/geral/planejamento.html": "app/templates/professor/planejamento/editor.html",
    "templates/geral/planejamentos.html": "app/templates/professor/planejamento/lista.html",
    "templates/list/listar_planos.html": "app/templates/professor/planejamento/todos_planos.html",
    "templates/intelligence.html": "app/templates/professor/planejamento/assistente_ia.html",
    "templates/add/add_atividade.html": "app/templates/professor/atividades/nova_atividade.html",
    "templates/edit/edit_atividade.html": "app/templates/professor/atividades/editar_atividade.html",
    "templates/list/listar_atividades.html": "app/templates/professor/atividades/listar_atividades.html",
    "templates/portal/dashboard_aluno.html": "app/templates/aluno/dashboard.html",
    "templates/portal/aguardando_turma.html": "app/templates/aluno/aguardando.html",
    "templates/portal/sem_acesso.html": "app/templates/aluno/sem_acesso.html",
    "templates/geral/aluno.html": "app/templates/aluno/perfil.html",
    "templates/edit/edit_perfil.html": "app/templates/components/perfil_usuario.html",
    "templates/security.html": "app/templates/components/security_check.html",
    "templates/geral/gerenciar_horario.html": "app/templates/admin/configuracoes/horario.html",

    # --- PYTHON CORE (Backend) ---
    "blueprints": "app/blueprints", # Move pasta inteira
    "models.py": "app/models/base_legacy.py", # Renomeia para legacy até refatorar
    "forms.py": "app/forms/forms_legacy.py",
    "utils.py": "app/utils/helpers.py",
    "extensions.py": "app/extensions.py",
    "config.py": "config.py", # Config fica na raiz ou move para app, depende da preferência. Vamos manter na raiz por enquanto.
    
    # --- STATIC & MEDIA ---
    "static/css": "app/static/css",
    "static/js": "app/static/js",
    "static/uploads": "media", # Move uploads para fora do código fonte
}

def make_backup():
    """Cria uma cópia completa de segurança antes de mexer."""
    print(f"📦 Criando backup de segurança em {BACKUP_DIR}...")
    try:
        # Copia tudo exceto a pasta de backup e .git
        shutil.copytree(BASE_DIR, BACKUP_DIR, ignore=shutil.ignore_patterns('backup_*', '.git', '__pycache__', 'venv', '.env'))
        print("✅ Backup concluído!")
    except Exception as e:
        print(f"❌ Erro no backup: {e}")
        input("Pressione Enter para continuar MESMO SEM BACKUP ou Ctrl+C para cancelar...")

def create_structure():
    """Cria as pastas vazias."""
    print("\n🏗️ Criando estrutura de pastas Enterprise...")
    for directory in NEW_DIRS:
        path = BASE_DIR / directory
        path.mkdir(parents=True, exist_ok=True)
        (path / "__init__.py").touch() # Transforma pastas em pacotes Python

def move_files():
    """Move os arquivos conforme o mapa."""
    print("\n🚚 Migrando arquivos...")
    
    for src_str, dest_str in MOVE_MAP.items():
        src = BASE_DIR / src_str
        dest = BASE_DIR / dest_str
        
        if src.exists():
            try:
                # Se for diretório e destino não existir, move direto
                if src.is_dir():
                    # Para diretórios, shutil.move tenta colocar dentro se já existir, então cuidado
                    if dest.exists():
                        # Se já existe, fundir é complexo, vamos mover o conteúdo
                        for item in src.iterdir():
                            shutil.move(str(item), str(dest))
                        shutil.rmtree(src)
                    else:
                        shutil.move(str(src), str(dest))
                else:
                    # Se for arquivo
                    if dest.exists():
                        print(f"⚠️ Arquivo já existe no destino: {dest_str} (Ignorado)")
                    else:
                        shutil.move(str(src), str(dest))
                
                print(f"✅ Movido: {src_str} -> {dest_str}")
            except Exception as e:
                print(f"❌ Erro ao mover {src_str}: {e}")
        else:
            print(f"ℹ️ Item não encontrado: {src_str} (Normal se já foi movido)")

def create_init_files():
    """Cria o __init__.py principal do app factory."""
    app_init = APP_DIR / "__init__.py"
    if not app_init.exists():
        print("\n🔧 Criando app/__init__.py (Application Factory)...")
        with open(app_init, "w", encoding="utf-8") as f:
            f.write('''
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
''')

if __name__ == "__main__":
    print("--- 🧠 REORGANIZAÇÃO CORTEX LUMINA (SAAS MODE) ---")
    make_backup()
    create_structure()
    move_files()
    create_init_files()
    print("\n🏁 Processo Finalizado!")
    print("⚠️  IMPORTANTE: O sistema agora está 'quebrado'.")
    print("1. Atualize os imports nos arquivos em 'app/blueprints/'.")
    print("2. Atualize 'run.py' para importar 'create_app' de 'app'.")
    print("3. Execute as migrações de banco se necessário.")
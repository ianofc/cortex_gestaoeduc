import os
from pathlib import Path

# Configuração
BASE_DIR = Path(".")
APP_DIR = BASE_DIR / "app"

# 1. Mapa de Correção de IMPORTAÇÕES PYTHON (Backend)
# "Texto Antigo": "Texto Novo"
PYTHON_FIXES = {
    # Módulos Movidos para app/
    "from models import": "from app.models.base_legacy import",
    "import models": "import app.models.base_legacy as models",
    "from forms import": "from app.forms.forms_legacy import",
    "import forms": "import app.forms.forms_legacy as forms",
    "from extensions import": "from app.extensions import",
    "from utils import": "from app.utils.helpers import",
    
    # Correção de Blueprints (se houver referências antigas)
    "blueprints.alunos": "app.blueprints.alunos",
    "blueprints.auth": "app.blueprints.auth",
    "blueprints.core": "app.blueprints.core",
    "blueprints.planos": "app.blueprints.planos",
    "blueprints.portal": "app.blueprints.portal",
}

# 2. Mapa de Correção de TEMPLATES (Frontend)
# Atualiza os caminhos nos render_template() e {% extends %}
TEMPLATE_FIXES = {
    # Layouts Base
    "main/base.html": "layouts/base_app.html",
    "main/index.html": "layouts/base_public.html",
    
    # Auth
    "main/login.html": "auth/login.html",
    "main/register.html": "auth/register.html",
    
    # Admin / Direção (Antigo Geral/Add/List/Edit)
    "geral/dashboard_global.html": "admin/dashboard/global.html",
    "geral/gerenciar_horario.html": "admin/configuracoes/horario.html",
    
    "add/add_escola.html": "admin/configuracoes/nova_escola.html",
    "edit/edit_escola.html": "admin/configuracoes/editar_escola.html",
    "list/listar_escola.html": "admin/configuracoes/listar_escolas.html",
    
    "add/add_professor.html": "admin/usuarios/novo_professor.html",
    "edit/edit_professor.html": "admin/usuarios/editar_professor.html",
    "list/listar_professores.html": "admin/usuarios/listar_professores.html",
    
    "add/add_aluno.html": "admin/usuarios/novo_aluno.html",
    "edit/edit_aluno.html": "admin/usuarios/editar_aluno.html",
    "list/listar_alunos.html": "admin/usuarios/listar_alunos.html",
    
    "add/add_turma.html": "admin/configuracoes/nova_turma.html",
    "edit/edit_turma.html": "admin/configuracoes/editar_turma.html",
    "list/listar_turmas.html": "admin/configuracoes/listar_turmas.html",
    
    # Professor
    "geral/dashboard_turma.html": "professor/dashboard/turma.html",
    "geral/diario_bordo.html": "professor/turma/diario_classe.html",
    "geral/gradebook.html": "professor/turma/gradebook.html",
    "geral/registrar_presenca.html": "professor/turma/chamada.html",
    "geral/gerar_prova.html": "professor/atividades/gerador_provas.html",
    "geral/turma.html": "professor/turma/visao_geral.html",
    
    "geral/planejamento.html": "professor/planejamento/editor.html",
    "geral/planejamentos.html": "professor/planejamento/lista.html",
    "list/listar_planos.html": "professor/planejamento/todos_planos.html",
    "intelligence.html": "professor/planejamento/assistente_ia.html",
    
    "add/add_atividade.html": "professor/atividades/nova_atividade.html",
    "edit/edit_atividade.html": "professor/atividades/editar_atividade.html",
    "list/listar_atividades.html": "professor/atividades/listar_atividades.html",
    
    # Aluno
    "portal/dashboard_aluno.html": "aluno/dashboard.html",
    "portal/aguardando_turma.html": "aluno/aguardando.html",
    "portal/sem_acesso.html": "aluno/sem_acesso.html",
    "geral/aluno.html": "aluno/perfil.html",
    
    # Site Público
    "landing_page.html": "public/landing_page.html",
    "pricing.html": "public/pricing.html",
    "contact.html": "public/contact.html",
    "demo.html": "public/demo.html",
    "checkout.html": "public/checkout.html",
}

def corrigir_arquivo(caminho):
    try:
        # Tenta ler como UTF-8
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except UnicodeDecodeError:
        # Se falhar, tenta latin-1 (comum em Windows antigo)
        with open(caminho, 'r', encoding='latin-1') as f:
            conteudo = f.read()
            
    novo_conteudo = conteudo
    modificado = False
    
    # Aplica correções Python se for .py
    if caminho.suffix == '.py':
        for velho, novo in PYTHON_FIXES.items():
            if velho in novo_conteudo:
                novo_conteudo = novo_conteudo.replace(velho, novo)
                modificado = True
                
    # Aplica correções de Template em TODOS os arquivos (Python chama templates, HTML estende templates)
    for velho, novo in TEMPLATE_FIXES.items():
        # Verifica aspas simples e duplas
        if f"'{velho}'" in novo_conteudo:
            novo_conteudo = novo_conteudo.replace(f"'{velho}'", f"'{novo}'")
            modificado = True
        if f'"{velho}"' in novo_conteudo:
            novo_conteudo = novo_conteudo.replace(f'"{velho}"', f'"{novo}"')
            modificado = True

    if modificado:
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)
        print(f"🔧 Corrigido: {caminho.name}")
    
def varrer_e_corrigir():
    print("🕵️  Iniciando varredura de correções...")
    count = 0
    
    # Percorre toda a pasta APP
    for root, dirs, files in os.walk(APP_DIR):
        for file in files:
            if file.endswith(('.py', '.html')):
                caminho = Path(root) / file
                corrigir_arquivo(caminho)
                count += 1
                
    # Verifica arquivos na raiz também (run.py, etc)
    for file in BASE_DIR.glob("*.py"):
        if file.name != "corrigir_referencias.py": # Não corrigir a si mesmo
            corrigir_arquivo(file)

    print(f"\n✅ Concluído! Verificados {count} arquivos.")
    print("Tente rodar 'python run.py' agora.")

if __name__ == "__main__":
    varrer_e_corrigir()
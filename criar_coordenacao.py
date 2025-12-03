import os
from pathlib import Path

BASE_DIR = Path("app")

# 1. Criar pastas de Templates da Coordenação
dirs_coord = [
    BASE_DIR / "templates/coordenacao/dashboard",
    BASE_DIR / "templates/coordenacao/pedagogico", # Ver planos, notas
    BASE_DIR / "templates/coordenacao/relatorios",
]

# 2. Criar pastas de Blueprint (Rotas)
blueprint_file = BASE_DIR / "blueprints/coordenacao.py"

def criar_estrutura():
    print("🚧 Criando Área da Coordenação...")
    
    # Criar pastas
    for d in dirs_coord:
        d.mkdir(parents=True, exist_ok=True)
        print(f"✅ Pasta criada: {d}")
        
        # Criar um arquivo dummy para a pasta não sumir
        (d / ".gitkeep").touch()

    # Criar um Dashboard Básico HTML
    dash_html = BASE_DIR / "templates/coordenacao/dashboard/index.html"
    if not dash_html.exists():
        with open(dash_html, "w", encoding="utf-8") as f:
            f.write("""{% extends "layouts/base_app.html" %}

{% block title %}Painel da Coordenação{% endblock %}

{% block content %}
<div class="p-6">
    <h1 class="text-2xl font-bold text-gray-800">🏫 Visão Pedagógica</h1>
    <div class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-white p-6 rounded-lg shadow">
            <h3 class="text-lg font-semibold">Planos Pendentes</h3>
            <p class="text-3xl font-bold text-yellow-600 mt-2">12</p>
            <p class="text-sm text-gray-500">Aguardando aprovação</p>
        </div>
    </div>
</div>
{% endblock %}
""")
        print(f"✅ Template criado: {dash_html}")

    # Criar o Blueprint Python
    if not blueprint_file.exists():
        with open(blueprint_file, "w", encoding="utf-8") as f:
            f.write("""from flask import Blueprint, render_template
from flask_login import login_required, current_user

# Define o Blueprint
coordenacao_bp = Blueprint('coordenacao', __name__, template_folder='templates')

@coordenacao_bp.before_request
@login_required
def check_permission():
    # Aqui vamos travar para só Coordenador ou Admin acessar
    # if not current_user.is_coordinator and not current_user.is_admin:
    #     return "Acesso Negado", 403
    pass

@coordenacao_bp.route('/coordenacao/dashboard')
def dashboard():
    return render_template('coordenacao/dashboard/index.html')

# Adicione mais rotas aqui (ex: aprovar_plano, ver_diario)
""")
        print(f"✅ Blueprint criado: {blueprint_file}")

    print("\n🚀 Concluído! Agora você tem a estrutura para a Coordenação.")
    print("⚠️ Lembre-se de registrar o blueprint 'coordenacao_bp' no arquivo app/__init__.py")

if __name__ == "__main__":
    criar_estrutura()
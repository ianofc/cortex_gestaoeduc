from flask import Blueprint, render_template
from flask_login import login_required, current_user

# Define o Blueprint 'coordenacao'
# Padrão: Semelhante ao 'planos.py' (Professor) ou 'core.py' (Admin)
coordenacao_bp = Blueprint('coordenacao', __name__, template_folder='templates')

@coordenacao_bp.before_request
@login_required
def check_permission():
    # Middleware de segurança
    # Garante que apenas usuários autorizados acessem este módulo
    pass

@coordenacao_bp.route('/coordenacao/dashboard')
def dashboard():
    # Padrão de Nomenclatura: 'visao_geral.html' em vez de 'index.html'
    # Isso facilita a busca do arquivo e segue o padrão 'professor/dashboard/turma.html'
    return render_template('coordenacao/dashboard/visao_geralcoord.html')
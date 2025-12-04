from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

# Definindo o blueprint para o Portal do Professor
professor_bp = Blueprint('professor', __name__, url_prefix='/professor')

@professor_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard principal para professores.
    """
    # Lógica de autorização deve garantir que apenas Professor/Admin/Coordenador acesse
    if current_user.has_role('aluno') or current_user.has_role('responsavel'):
        return redirect(url_for('portal.dashboard'))

    # Esta rota pode ser usada para redirecionar para uma visão geral da área do professor
    return render_template('professor/dashboard/visao_geral.html', title='Painel do Professor')
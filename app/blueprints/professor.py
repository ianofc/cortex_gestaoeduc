from flask import Blueprint, redirect, url_for
from flask_login import login_required

# Definindo o blueprint para o Portal do Professor
professor_bp = Blueprint('professor', __name__, url_prefix='/professor')

@professor_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Rota legada do dashboard do professor.
    Redireciona para o dashboard central em core.py que carrega todos os dados corretos.
    """
    return redirect(url_for('core.dashboard'))